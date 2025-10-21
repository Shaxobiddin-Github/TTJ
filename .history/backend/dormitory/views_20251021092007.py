from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Building, Room, Activity
from student.models import Student, StudentPaymentStory
from .serializers import (
	BuildingSerializer,
	BuildingSummarySerializer,
	RoomSerializer,
	RoomListSerializer,
	StudentSerializer,
	ActivitySerializer,
)
from drf_yasg.utils import swagger_auto_schema
from django.utils import timezone
from django.db.models import Sum, Max, OuterRef, Subquery, Q, Count
from datetime import timedelta
from rest_framework.permissions import IsAuthenticated
from .permissions import HasRequiredDjangoPerms


class DashboardView(APIView):
	permission_classes = [IsAuthenticated, HasRequiredDjangoPerms]
	permission_required = ["dormitory.can_view_dashboard"]
	@swagger_auto_schema(operation_description="Dashboard statistikalarini qaytaradi")
	def get(self, request):
		today = timezone.localdate()
		now = timezone.now()

		total_students = Student.objects.count() # jami talabalar soni
		total_rooms = Room.objects.count() # jami xonalar soni
		total_buildings = Building.objects.count() # jami binolar soni

		total_capacity = Room.objects.aggregate(total=Sum('capacity'))['total'] or 0 # jami sig'im
		assigned_students = Student.objects.exclude(room__isnull=True).count() # xonaga joylashgan talabalar soni
		occupancy_rate = round((assigned_students / total_capacity) * 100, 1) if total_capacity else 0.0 # bandlik foizi

		# Students inside/outside (oxirgi activity bo'yicha)
		last_action_sq = Activity.objects.filter(student=OuterRef('pk')).order_by('-time').values('action')[:1] # oxirgi harakat
		students_inside = Student.objects.annotate(last_action=Subquery(last_action_sq))\
			.filter(last_action__in=['in', 'late_in']).count()  # oxirgi harakati 'in' yoki 'late_in' bo'lganlar
		students_outside = max(total_students - students_inside, 0) # tashqarida bo'lganlar

		# Contracts expiring in 7 days
		in_7_days = today + timedelta(days=7) # 7 kun ichida tugaydigan shartnomalar
		expiring_qs = Student.objects.filter(contract_end__gte=today, contract_end__lte=in_7_days) # 7 kun ichida tugaydigan shartnomalar
		expiring_contracts_7_days = expiring_qs.count() # soni
		expiring_list = [
			{
				'student_id': s.student_id,  
				'full_name': f"{s.last_name} {s.first_name}",
				'contract_end': s.contract_end,
			} 
			for s in expiring_qs.order_by('contract_end')[:10]
		] # ro'yxat (maks 10 ta)

		# Late today
		late_today_count = Activity.objects.filter(action='late_in', time__date=today).count() # bugun kechikkanlar

		# Today activities
		today_activity_count = Activity.objects.filter(time__date=today).count() # bugungi faolliklar soni

		# Active students last 24h
		last24 = now - timedelta(hours=24) # oxirgi 24 soat ichida harakat qilgan talabalar
		active_students_24h = Student.objects.filter(activities__time__gte=last24).distinct().count() # soni

		# Pending payments: oxirgi to'lov 30 kundan eski yoki yo'q
		last_pay_sq = StudentPaymentStory.objects.filter(student=OuterRef('pk')).order_by()\
			.values('student').annotate(latest=Max('date')).values('latest')[:1] # oxirgi to'lov sanasi
		pending_payments = Student.objects.annotate(last_payment=Subquery(last_pay_sq))\
			.filter(Q(last_payment__isnull=True) | Q(last_payment__lt=today - timedelta(days=30))).count() # soni

		# Recent activities
		recent = Activity.objects.select_related('student', 'student__room', 'student__room__building')\
			.order_by('-time')[:10] # oxirgi 10 ta faollik
		recent_activities = []  
		for a in recent:
			room = getattr(a.student, 'room', None)
			recent_activities.append({
				'student_id': a.student.student_id,
				'full_name': f"{a.student.last_name} {a.student.first_name}",
				'action': a.action,
				'time': a.time,
				'room_number': room.number if room else None,
				'building': room.building.name if room else None,
			})

		# Cards for UI (exact labels as screenshot)
		cards = [
			{'key': 'total_students', 'label': 'Jami talabalar', 'value': total_students},
			{'key': 'total_rooms', 'label': 'Yotoqxona xonalari', 'value': total_rooms},
			{'key': 'students_inside', 'label': 'Hozir ichkarida', 'value': students_inside},
			{'key': 'students_outside', 'label': 'Tashqarida', 'value': students_outside},
		]

		# Alerts (ogohlantirishlar)
		alerts = []
		if expiring_contracts_7_days:
			alerts.append({
				'text': f"{expiring_contracts_7_days} ta talabaning shartnomasi 7 kun ichida tugaydi",
				'variant': 'warning',  # info|warning|danger
			})
		if late_today_count:
			alerts.append({
				'text': f"{late_today_count} ta talaba bugun kechikib kirdi",
				'variant': 'info',
			})
		if pending_payments:
			alerts.append({
				'text': f"{pending_payments} ta talabada 30 kundan beri to'lov yo'q",
				'variant': 'danger',
			})

		# Normalize recent activities for table: Vaqt, Talaba, Harakat, Xona
		normalized_recent = []
		for a in recent:
			room = getattr(a.student, 'room', None)
			local_dt = timezone.localtime(a.time)
			normalized_recent.append({
				'time': local_dt.strftime('%H:%M'),
				'student': f"{a.student.first_name} {a.student.last_name}",
				'action': a.get_action_display(),
				'room': room.number if room else None,
			})

		data = {
			'cards': cards,
			'alerts': alerts,
			'recent_activities': normalized_recent,
			# Raw metrics for additional widgets/analytics
			'metrics': {
				'total_students': total_students,
				'total_rooms': total_rooms,
				'total_buildings': total_buildings,
				'students_inside': students_inside,
				'students_outside': students_outside,
				'occupancy_rate': occupancy_rate,
				'today_activity_count': today_activity_count,
				'late_today_count': late_today_count,
				'pending_payments': pending_payments,
				'expiring_contracts_7_days': expiring_contracts_7_days,
				'active_students_24h': active_students_24h,
			},
			# Extra detailed list for expiring contracts card
			'expiring_contracts': expiring_list,
		}

		return Response(data)


# Bino va Xonalar sahifasi uchun alohida view (page-specific payload)
class BinoXonalarView(APIView):
	@swagger_auto_schema(operation_description="Bino va Xonalar sahifasi uchun ma'lumotlar (binolar kartalari va xonalar jadvali)")
	def get(self, request):


		# Binolar: kartochkalar uchun qisqa ma'lumot
		buildings_qs = Building.objects.all().annotate(rooms_total=Count('rooms')) # har bir binoda xonalar soni bilan
		buildings_data = BuildingSummarySerializer(buildings_qs, many=True).data 

		# Xonalar: jadval uchun ma'lumot, optional filter: ?building=<id>&status=
		rooms_qs = Room.objects.all().annotate(occupied=Count('students')) # har bir xonada joylashgan talabalar soni bilan
		building_id = request.GET.get('building') # filter parametrlari
		status_param = request.GET.get('status') # empty|partial|full
		if building_id:
			rooms_qs = rooms_qs.filter(building_id=building_id) # binoga ko'ra filter
		if status_param:
			rooms_qs = rooms_qs.filter(status=status_param) # bandlik holatiga ko'ra filter
		rooms_data = RoomListSerializer(rooms_qs, many=True).data # serializatsiya

		return Response({
			'buildings': buildings_data,
			'rooms': rooms_data,
		})

# Building CRUD
class BuildingListCreate(APIView):
	@swagger_auto_schema(
		manual_parameters=[],
		operation_description="Barcha binolar. Optional: ?name=substring",
	)
	def get(self, request):
		qs = Building.objects.all().annotate(rooms_total=Count('rooms'))
		name = request.GET.get('name')
		if name:
			qs = qs.filter(name__icontains=name)
		serializer = BuildingSummarySerializer(qs, many=True)
		return Response(serializer.data)

	"""
	get:
	Barcha binolar ro'yxatini qaytaradi.
	post:
	Yangi bino qo'shadi.
	"""
	@swagger_auto_schema(responses={200: BuildingSerializer(many=True)})
	def post(self, request):
		serializer = BuildingSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	
	@swagger_auto_schema(
		operation_description="Barcha binolar ro'yxatini qaytaradi",
		responses={200: BuildingSerializer(many=True)}
	)
	def get(self, request):
		"""
		GET: Barcha binolar ro'yxatini JSON ko'rinishida qaytaradi.
		"""
		buildings = Building.objects.all()
		serializer = BuildingSerializer(buildings, many=True)
		return Response(serializer.data)

	@swagger_auto_schema(
		operation_description="Yangi bino qo'shish",
		request_body=BuildingSerializer,
		responses={201: BuildingSerializer},
		examples={
			'application/json': {
				"name": "Bino nomi",
				"floors": 3,
				"rooms_count": 20,
				"capacity": 120
			}
		}
	)
	def post(self, request):
		"""
		POST: Yangi bino qo'shish uchun quyidagi maydonlarni yuboring:
		{
			"name": "Bino nomi",
			"floors": 3,
			"rooms_count": 20,
			"capacity": 120
		}
		"""
		serializer = BuildingSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BuildingDetail(APIView):
	def get_object(self, pk):
		try:
			return Building.objects.get(pk=pk)
		except Building.DoesNotExist:
			return None

	def get(self, request, pk):
		building = self.get_object(pk)
		if not building:
			return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
		serializer = BuildingSerializer(building)
		return Response(serializer.data)

	"""
	get:
	Bino tafsilotlarini qaytaradi.
	put:
	Binoni yangilaydi.
	delete:
	Binoni o'chiradi.
	"""
	
	# Docstring faqat metod ichida bo'lishi kerak
	@swagger_auto_schema(responses={200: BuildingSerializer})
	def put(self, request, pk):
		building = self.get_object(pk)
		if not building:
			return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
		serializer = BuildingSerializer(building, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	@swagger_auto_schema(responses={204: 'Deleted'})
	def delete(self, request, pk):
		building = self.get_object(pk)
		if not building:
			return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
		building.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)

# Room CRUD
class RoomListCreate(APIView):
	@swagger_auto_schema(
		operation_description="Barcha xonalar. Optional: ?building=<id>&status=empty|partial|full",
	)
	def get(self, request):
		qs = Room.objects.all().annotate(occupied=Count('students'))
		building_id = request.GET.get('building')
		status_param = request.GET.get('status')
		if building_id:
			qs = qs.filter(building_id=building_id)
		if status_param:
			qs = qs.filter(status=status_param)
		serializer = RoomListSerializer(qs, many=True)
		return Response(serializer.data)

	"""
	get:
	Barcha xonalar ro'yxatini qaytaradi.
	post:
	Yangi xona qo'shadi.
	"""
	@swagger_auto_schema(responses={200: RoomSerializer(many=True)})
	def post(self, request):
		serializer = RoomSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	
	"""
	GET: Barcha xonalar ro'yxatini JSON ko'rinishida qaytaradi.
	POST: Yangi xona qo'shish uchun quyidagi maydonlarni yuboring:
	{
		"building": 1,
		"number": "101",
		"floor": 1,
		"capacity": 6,
		"status": "empty"
	}
	"""

class RoomDetail(APIView):
	def get_object(self, pk):
		try:
			return Room.objects.get(pk=pk)
		except Room.DoesNotExist:
			return None

	def get(self, request, pk):
		room = self.get_object(pk)
		if not room:
			return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
		serializer = RoomSerializer(room)
		return Response(serializer.data)

	"""
	get:
	Xona tafsilotlarini qaytaradi.
	put:
	Xonani yangilaydi.
	delete:
	Xonani o'chiradi.
	"""
	@swagger_auto_schema(responses={200: RoomSerializer})
	def put(self, request, pk):
		room = self.get_object(pk)
		if not room:
			return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
		serializer = RoomSerializer(room, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	@swagger_auto_schema(responses={204: 'Deleted'})
	def delete(self, request, pk):
		room = self.get_object(pk)
		if not room:
			return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
		room.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)

# Student CRUD
class StudentListCreate(APIView):
	@swagger_auto_schema(
		operation_description="Talabalar. Optional: ?student_id=...&name=substring",
	)
	def get(self, request):
		qs = Student.objects.all()
		student_id = request.GET.get('student_id')
		name = request.GET.get('name')
		if student_id:
			qs = qs.filter(student_id=student_id)
		if name:
			qs = qs.filter(first_name__icontains=name) | qs.filter(last_name__icontains=name)
		serializer = StudentSerializer(qs, many=True)
		return Response(serializer.data)

	"""
	get:
	Barcha talabalar ro'yxatini qaytaradi.
	post:
	Yangi talaba qo'shadi.
	"""
	@swagger_auto_schema(responses={200: StudentSerializer(many=True)})
	def post(self, request):
		serializer = StudentSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	
	"""
	GET: Barcha talabalar ro'yxatini JSON ko'rinishida qaytaradi.
	POST: Yangi talaba qo'shish uchun quyidagi maydonlarni yuboring:
	{
		"student_id": "20250001",
		"first_name": "Ali",
		"last_name": "Valiyev",
		"room": 1,
		"contract_end": "2025-12-31"
	}
	"""

class StudentDetail(APIView):
	def get_object(self, pk):
		try:
			return Student.objects.get(pk=pk)
		except Student.DoesNotExist:
			return None

	def get(self, request, pk):
		student = self.get_object(pk)
		if not student:
			return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
		serializer = StudentSerializer(student)
		return Response(serializer.data)

	"""
	get:
	Talaba tafsilotlarini qaytaradi.
	put:
	Talabani yangilaydi.
	delete:
	Talabani o'chiradi.
	"""
	@swagger_auto_schema(responses={200: StudentSerializer})
	def put(self, request, pk):
		student = self.get_object(pk)
		if not student:
			return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
		serializer = StudentSerializer(student, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	@swagger_auto_schema(responses={204: 'Deleted'})
	def delete(self, request, pk):
		student = self.get_object(pk)
		if not student:
			return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
		student.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)

# Activity CRUD
class ActivityListCreate(APIView):
	@swagger_auto_schema(
		operation_description="Faolliklar. Optional: ?action=in|out|late_in|absent",
	)
	def get(self, request):
		qs = Activity.objects.all()
		action = request.GET.get('action')
		if action:
			qs = qs.filter(action=action)
		serializer = ActivitySerializer(qs, many=True)
		return Response(serializer.data)

	"""
	get:
	Barcha faolliklar ro'yxatini qaytaradi.
	post:
	Yangi faollik qo'shadi.
	"""
	@swagger_auto_schema(responses={200: ActivitySerializer(many=True)})
	def post(self, request):
		serializer = ActivitySerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	
	"""
	GET: Barcha faolliklar ro'yxatini JSON ko'rinishida qaytaradi.
	POST: Yangi faollik qo'shish uchun quyidagi maydonlarni yuboring:
	{
		"student": 1,
		"time": "2025-09-19T12:00:00Z",
		"action": "in"
	}
	"""

class ActivityDetail(APIView):
	def get_object(self, pk):
		try:
			return Activity.objects.get(pk=pk)
		except Activity.DoesNotExist:
			return None

	def get(self, request, pk):
		activity = self.get_object(pk)
		if not activity:
			return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
		serializer = ActivitySerializer(activity)
		return Response(serializer.data)

	"""
	get:
	Faollik tafsilotlarini qaytaradi.
	put:
	Faollikni yangilaydi.
	delete:
	Faollikni o'chiradi.
	"""
	@swagger_auto_schema(responses={200: ActivitySerializer})
	def put(self, request, pk):
		activity = self.get_object(pk)
		if not activity:
			return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
		serializer = ActivitySerializer(activity, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	@swagger_auto_schema(responses={204: 'Deleted'})
	def delete(self, request, pk):
		activity = self.get_object(pk)
		if not activity:
			return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
		activity.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)
