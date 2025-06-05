from django.contrib import admin
from django.urls import path
from sait.views import *


urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('colors/', color_settings, name='color_settings'),
    path('upload/', upload_file, name='upload'),
    path('vedomosti/', vedomosti_list, name='vedomosti_list'),
    path('grades/<int:vedomost_id>/', grades_view, name='grades'),
    path('vedomosti/delete/<int:ved_id>/', delete_vedomost, name='delete_vedomost'),
    path('create-teacher/', create_teacher, name='create_teacher'),
    path('colors/ta/', color_settings_ta, name='color_settings_ta'),
    path('upload_teacher_assignments/', upload_teacher_assignments, name='upload_teacher_assignments'),
    path('generate-report/', generate_report_view, name='generate_report'),
    path('ajax/get-years-by-entity/', ajax_get_years_by_entity, name='ajax_get_years_by_entity'),
    path('users/', users_list, name='users_list'),
    path('users/<int:user_id>/edit/', edit_user, name='edit_user'),
    path('users/<int:user_id>/delete/', delete_user, name='delete_user'),
    path('delete-teacher-assignment/<int:pk>/', delete_teacher_assignment, name='delete_teacher_assignment'),

]