from django.urls import path
from .views import (
    BuildingListCreate, BuildingDetail,
    RoomListCreate, RoomDetail,
    StudentListCreate, StudentDetail,
    ActivityListCreate, ActivityDetail
)

urlpatterns = [
    path('buildings/', BuildingListCreate.as_view(), name='building-list-create'),
    path('buildings/<int:pk>/', BuildingDetail.as_view(), name='building-detail'),

    path('rooms/', RoomListCreate.as_view(), name='room-list-create'),
    path('rooms/<int:pk>/', RoomDetail.as_view(), name='room-detail'),

    path('students/', StudentListCreate.as_view(), name='student-list-create'),
    path('students/<int:pk>/', StudentDetail.as_view(), name='student-detail'),

    path('activities/', ActivityListCreate.as_view(), name='activity-list-create'),
    path('activities/<int:pk>/', ActivityDetail.as_view(), name='activity-detail'),
]
