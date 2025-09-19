from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Building, Room, Student, Activity
from .serializers import BuildingSerializer, RoomSerializer, StudentSerializer, ActivitySerializer
from drf_yasg.utils import swagger_auto_schema

# Building CRUD
class BuildingListCreate(APIView):
	def get(self, request):
		buildings = Building.objects.all()
		serializer = BuildingSerializer(buildings, many=True)
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
	def get(self, request):
		rooms = Room.objects.all()
		serializer = RoomSerializer(rooms, many=True)
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
	def get(self, request):
		students = Student.objects.all()
		serializer = StudentSerializer(students, many=True)
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
	def get(self, request):
		activities = Activity.objects.all()
		serializer = ActivitySerializer(activities, many=True)
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
