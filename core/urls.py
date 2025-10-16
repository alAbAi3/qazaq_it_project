from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('', views.index, name='index'),
    path('course/<int:pk>/', views.course_detail, name='course_detail'), # 👈 Осы жолды қосыңыз
    path('course/<int:course_pk>/lesson/<int:lesson_pk>/', views.lesson_detail, name='lesson_detail'),
    path('courses/', views.course_list, name='course_list'),
    path('jobs/', views.job_list, name='job_list'),    
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),    
    path('profile/', views.profile, name='profile'),
    path('course/<int:pk>/enroll/', views.enroll_course, name='enroll_course'),
    path('course/<int:pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('my-favorites/', views.my_favorites, name='my_favorites'),
    path('course/<int:pk>/checkout/', views.checkout, name='checkout'),
    path('job/<int:pk>/', views.job_detail, name='job_detail'),
    path('schedule/', views.schedule, name='schedule'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('course/<int:pk>/purchase-success/', views.purchase_success, name='purchase_success'),
    path('my-courses/', views.my_courses, name='my_courses'),
]