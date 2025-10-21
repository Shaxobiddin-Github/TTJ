
from django.db import models

# Create your models here.

class Student(models.Model):  # Talaba modeli: yotoqxonadagi talabalar haqida
 student_id = models.CharField(max_length=20, unique=True)  # Talaba ID raqami
 picture = models.ImageField(upload_to='student_pics/', null=True, blank=True)  # Talaba rasmi
 first_name = models.CharField(max_length=50)  # Ismi
 last_name = models.CharField(max_length=50)   # Familiyasi
 third_name = models.CharField(max_length=50, null=True, blank=True)  # Otasining ismi
 birth_date = models.DateField(null=True, blank=True)  # Tug‘ilgan sanasi
 phone_number = models.CharField(max_length=15, null=True, blank=True)  # Telefon raqami    
 parent_contact = models.CharField(max_length=15, null=True, blank=True)  # Ota-ona yoki vasiy telefon raqami
 address = models.TextField(null=True, blank=True)  # Manzil
 # Xona bilan bog'lanish (dormitory.Room ga FK). related_name='students' xonadagi talabalar sanog'ini olish uchun ishlatiladi
 room = models.ForeignKey('dormitory.Room', on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
 contact_start = models.DateField(null=True, blank=True)  # Shartnoma boshlanish sanasi
 contract_end = models.DateField(null=True, blank=True)  # Shartnoma tugash sanasi
 working_status = models.BooleanField(default=True)  # Faol yoki faol emasligi
 avg_gpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)  # O'rtacha baho
 avg_grade = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)  # O'rtacha baho 
 total_credits = models.PositiveIntegerField(null=True, blank=True)  # Umumiy kreditlar soni
 province = models.CharField(max_length=100, null=True, blank=True)  # Viloyat
 district = models.CharField(max_length=100, null=True, blank=True)  # Tuman
 paymentForm = models.CharField(max_length=100, null=True, blank=True)  # To'lov shakli
 department = models.CharField(max_length=100, null=True, blank=True)  # Fakultet
 group = models.CharField(max_length=100, null=True, blank=True)  # Guruh
 specialty = models.CharField(max_length=100, null=True, blank=True)  # Mutaxassislik
 def __str__(self):
  return f"{self.last_name} {self.first_name}"



class StudentPaymentStory(models.Model):  # To'lovlar tarixi modeli: talabalar to'lovlari haqida
 student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments')  # Qaysi talaba
 amount = models.DecimalField(max_digits=10, decimal_places=2)  # To'lov summasi
 payment_receipt = models.FileField(upload_to='payment_receipts/', null=True, blank=True)  # To'lov kvitansiyasi
 date = models.DateField()  # To'lov sanasi
 notes = models.TextField(null=True, blank=True)  # Qo'shimcha eslatmalar

 def __str__(self):
  return f"{self.student} - {self.amount} on {self.date}"
