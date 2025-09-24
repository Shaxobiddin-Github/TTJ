from rest_framework import serializers
from .models import Building, Room, Student, Activity

class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = '__all__'


class BuildingSummarySerializer(serializers.ModelSerializer):
    rooms_total = serializers.SerializerMethodField()

    class Meta:
        model = Building
        fields = ('id', 'name', 'floors', 'capacity', 'rooms_total')

    def get_rooms_total(self, obj):
        # Prefer DB annotation if present to avoid N+1
        return getattr(obj, 'rooms_total', obj.rooms.count())

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'


class RoomListSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source='building.name', read_only=True)
    occupied = serializers.SerializerMethodField()
    status_label = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = (
            'id', 'number', 'building', 'building_name', 'floor', 'capacity',
            'occupied', 'status', 'status_label'
        )

    def get_occupied(self, obj):
        return getattr(obj, 'occupied', obj.students.count())

    def get_status_label(self, obj):
        return obj.get_status_display()

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = '__all__'
