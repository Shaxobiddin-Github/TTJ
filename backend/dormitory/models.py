from django.db import models

class Building(models.Model):  # Bino modeli: yotoqxona binosi haqida ma'lumot
	name = models.CharField(max_length=100)  # Bino nomi
	floors = models.PositiveIntegerField()  # Qavatlar soni
	rooms_count = models.PositiveIntegerField()  # Xonalar soni
	capacity = models.PositiveIntegerField()  # Binoning umumiy sig‘imi

	def __str__(self):
		return self.name

class Room(models.Model):  # Xona modeli: har bir xonaning parametrlari
	building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='rooms')  # Qaysi binoga tegishli
	number = models.CharField(max_length=10)  # Xona raqami
	floor = models.PositiveIntegerField()  # Qavat raqami
	capacity = models.PositiveIntegerField()  # Xona sig‘imi
	STATUS_CHOICES = [
		('full', 'To’la'),        # Xona to‘la
		('partial', 'Qisman band'), # Qisman band
		('empty', 'Bo’sh'),      # Bo‘sh
	]
	status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='empty')  # Bandlik holati

	def __str__(self):
		return f"{self.building.name} - {self.number}"

class Student(models.Model):  # Talaba modeli: yotoqxonadagi talabalar haqida
	student_id = models.CharField(max_length=20, unique=True)  # Talaba ID raqami
	first_name = models.CharField(max_length=50)  # Ismi
	last_name = models.CharField(max_length=50)   # Familiyasi
	room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')  # Qaysi xonada joylashgan
	contract_end = models.DateField(null=True, blank=True)  # Shartnoma tugash sanasi

	def __str__(self):
		return f"{self.last_name} {self.first_name}"

class Activity(models.Model):  # Faolliklar modeli: talabalar harakatlari logi
	student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='activities')  # Qaysi talaba
	time = models.DateTimeField()  # Harakat vaqti
	ACTION_CHOICES = [
		('in', 'Kirdi'),         # Kirgan
		('out', 'Chiqdi'),       # Chiqgan
		('late_in', 'Kech kirdi'), # Kech kirgan
		('absent', 'Umuman kirmadi'), # Umuman kirmagan
	]
	action = models.CharField(max_length=10, choices=ACTION_CHOICES)  # Harakat turi

	def __str__(self):
		return f"{self.student} - {self.get_action_display()} - {self.time}"
