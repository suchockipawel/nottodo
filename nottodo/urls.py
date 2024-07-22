from django.urls import path
from . import views

urlpatterns = [
    path('nottodos/', views.list_nottodos, name='list_nottodos'),
    path('nottodos/add/', views.add_nottodo, name='add_nottodo'),
    path('nottodos/update/<int:pk>/', views.update_nottodo, name='update_nottodo'),
    path('nottodos/delete/<int:pk>/', views.delete_nottodo, name='delete_nottodo'),
    path('nottodos/share/<int:pk>/', views.share_nottodo, name='share_nottodo'),
    path('nottodos/shared/', views.list_shared_nottodos, name='list_shared_nottodos'),
    path('nottodos/comment/<int:shared_nottodo_id>/', views.add_comment, name='add_comment'),
    path('nottodos/copy/<int:pk>/', views.copy_nottodo, name='copy_nottodo'),
    path('nottodos/unshare/<int:pk>/', views.unshare_nottodo, name='unshare_nottodo'),
    path('nottodos/<int:pk>/', views.view_nottodo, name='view_nottodo'),
    path('nottodos/events/', views.nottodo_events, name='nottodo_events'),
    path('change_email/', views.change_email, name='change_email'),
    path('change_password/', views.change_password, name='change_password'),
    path('profile/', views.profile, name='profile'),
    path('', views.home, name='home'),
    path('check_reminders/', views.check_reminders, name='check_reminders'),
]
