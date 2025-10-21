from django.contrib import admin
from .models import Building, Room, Activity, Role, UserProfile
from student.models import Student

@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
	list_display = ('name', 'floors', 'rooms_count', 'capacity')
	search_fields = ('name',)

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
	list_display = ('number', 'building', 'floor', 'capacity', 'status')
	list_filter = ('building', 'floor', 'status')
	search_fields = ('number',)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
	list_display = ('student_id', 'last_name', 'first_name', 'room', 'contract_end')
	list_filter = ('room', 'contract_end')
	search_fields = ('student_id', 'last_name', 'first_name')

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
	list_display = ('student', 'action', 'time')
	list_filter = ('action', 'time')
	search_fields = ('student__last_name', 'student__first_name')


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
	list_display = ('name', 'code')
	search_fields = ('name', 'code')
	filter_horizontal = ('permissions',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
	list_display = ('user',)
	search_fields = ('user__username', 'user__email')
	filter_horizontal = ('roles',)
