from django.db import models
from django.conf import settings
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import Permission


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
 picture = models.ImageField(upload_to='student_pics/', null=True, blank=True)  # Talaba rasmi
 first_name = models.CharField(max_length=50)  # Ismi
 last_name = models.CharField(max_length=50)   # Familiyasi
 third_name = models.CharField(max_length=50, null=True, blank=True)  # Otasining ismi
 birth_date = models.DateField(null=True, blank=True)  # Tug‘ilgan sanasi
 phone_number = models.CharField(max_length=15, null=True, blank=True)  # Telefon raqami
 parent_contact = models.CharField(max_length=15, null=True, blank=True)  # Ota-ona yoki vasiy telefon raqami
 address = models.TextField(null=True, blank=True)  # Manzil
 room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')  # Qaysi xonada joylashgan
 contact_start = models.DateField(null=True, blank=True)  # Shartnoma boshlanish sanasi
 contract_end = models.DateField(null=True, blank=True)  # Shartnoma tugash sanasi
 working_status = models.BooleanField(default=True)  # Faol yoki faol emasligi

 def __str__(self):
  return f"{self.last_name} {self.first_name}"

class Activity(models.Model):  # Faolliklar modeli: talabalar harakatlari logi
 student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='activities')  # Qaysi talaba
 time = models.DateTimeField(auto_now=True)  # Harakat vaqti
 ACTION_CHOICES = [
  ('in', 'Kirdi'),         # Kirgan
  ('out', 'Chiqdi'),       # Chiqgan
  ('late_in', 'Kech kirdi'), # Kech kirgan
  ('absent', 'Umuman kirmadi'), # Umuman kirmagan
 ]
 action = models.CharField(max_length=10, choices=ACTION_CHOICES)  # Harakat turi

 def __str__(self):
  return f"{self.student} - {self.get_action_display()} - {self.time}"


class TimeOpenEndClosed(models.Model):  # Yotoqxonani ochish va yopish vaqtlari
 open_time = models.TimeField()  # Ochilish vaqti
 close_time = models.TimeField()  # Yopilish vaqti

 def __str__(self):
  return f"Open: {self.open_time}, Close: {self.close_time}"

class StudentPaymentStory(models.Model):  # To'lovlar tarixi modeli: talabalar to'lovlari haqida
 student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments')  # Qaysi talaba
 amount = models.DecimalField(max_digits=10, decimal_places=2)  # To'lov summasi
 payment_receipt = models.FileField(upload_to='payment_receipts/', null=True, blank=True)  # To'lov kvitansiyasi
 date = models.DateField()  # To'lov sanasi
 notes = models.TextField(null=True, blank=True)  # Qo'shimcha eslatmalar

 def __str__(self):
  return f"{self.student} - {self.amount} on {self.date}"





# -------------------------------------------------------------------- AUTH--------------------------------------


# Rollar va foydalanuvchi profili
class Role(models.Model):
 name = models.CharField(max_length=50, unique=True)  # Masalan: Admin, Nazoratchi, Qo'riqchi, Hisobchi, Talaba
 code = models.SlugField(max_length=50, unique=True)  # Masalan: admin, warden, security, accountant, student
 permissions = models.ManyToManyField(
  Permission,
  related_name='roles',
  blank=True,
  help_text="Ushbu rolga beriladigan ruxsatlar (Django permissions)",
 )

 def __str__(self):
  return self.name


class UserProfile(models.Model):
 user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
 roles = models.ManyToManyField(Role, related_name='users', blank=True)
 # ixtiyoriy bog'lanish: talaba profili bilan tirish
 student = models.OneToOneField(Student, on_delete=models.SET_NULL, null=True, blank=True, related_name='user_profile')

 def __str__(self):
  return f"Profile of {getattr(self.user, 'username', 'user')}"

 class Meta:
  permissions = (
   ("can_view_dashboard", "Dashboardni ko'rish huquqi"),
   ("can_manage_dormitory", "Yotoqxona ma'lumotlarini boshqarish"),
  )


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
 if created:
  UserProfile.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
 # Profil mavjud bo'lmasa yaratishga urinmaymiz (create signal allaqachon yaratadi)
 try:
  instance.profile.save()
 except UserProfile.DoesNotExist:
  UserProfile.objects.create(user=instance)


# ---------- Roles -> User permissions sinxronizatsiyasi ----------
def sync_user_permissions(user):
 """
 Foydalanuvchi rollaridan kelib chiqib user.user_permissions ni yangilaydi.
 Superuser uchun hech narsa qilmaymiz (u allaqachon hamma ruxsatga ega).
 """
 # Ba'zi hollarda profil hali yaratilmagan bo'lishi mumkin
 profile = getattr(user, 'profile', None)
 if user.is_superuser or profile is None:
  return

 # Foydalanuvchi rollaridan yig'ilgan ruxsatlar to'plami
 roles_qs = profile.roles.all()
 perms = Permission.objects.filter(roles__in=roles_qs).distinct()
 user.user_permissions.set(perms)


@receiver(m2m_changed, sender=UserProfile.roles.through)
def on_user_roles_changed(sender, instance, action, reverse, model, pk_set, **kwargs):
 # Rollar qo'shilganda/olib tashlanganda/clear qilinganda user permissionsni yangilaymiz
 if action in {"post_add", "post_remove", "post_clear"}:
  sync_user_permissions(instance.user)


@receiver(m2m_changed, sender=Role.permissions.through)
def on_role_permissions_changed(sender, instance, action, reverse, model, pk_set, **kwargs):
 # Rolga ruxsatlar o'zgarsa, ushbu rol biriktirilgan barcha foydalanuvchilarning ruxsatlarini yangilaymiz
 if action in {"post_add", "post_remove", "post_clear"}:
  for profile in instance.users.select_related('user').all():
   sync_user_permissions(profile.user)


# --------------------------