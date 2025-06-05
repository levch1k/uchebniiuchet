from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import os

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('teacher', 'Преподаватель'),
        ('deputy', 'Завуч'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='teacher')

    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    middle_name = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.get_role_display()})"


class ColorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_color = models.CharField(max_length=7, default='#F01D18')
    subject_color = models.CharField(max_length=7, default='#4C3ACE')
    grade_color = models.CharField(max_length=7, default='#48D5E4')  # Новое поле для оценок
    group_color = models.CharField(max_length=7, default='#FFA500')  # Новое поле для цвета группы
    period_color = models.CharField(max_length=7, default='#008000')  # Новое поле для цвета периода

    ta_subject_color = models.CharField("Цвет дисциплины (СП)", max_length=7,
                                        default='#FFD700')
    ta_teacher_color = models.CharField("Цвет преподавателя (СП)", max_length=7,
                                        default='#00BFFF')
    ta_group_color = models.CharField("Цвет группы (СП)", max_length=7,
                                      default='#ADFF2F')
    def __str__(self):
        return f"Color Profile for {self.user.username}"



class Student(models.Model):
    """Студент."""
    full_name = models.CharField(max_length=255)
    group = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


class Vedomost(models.Model):
    SEMESTER_CHOICES = [
        ('1', 'Первый семестр'),
        ('2', 'Второй семестр'),
    ]

    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='vedomosti/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    upload_date = models.DateTimeField(auto_now_add=True)
    group_name = models.CharField(max_length=100, blank=True, null=True)  # Название группы
    semester = models.CharField(max_length=1, choices=SEMESTER_CHOICES, blank=True, null=True)  # Семестр
    academic_year = models.CharField(max_length=9, blank=True, null=True)  # Формат: 2023-2024
    data_hash = models.CharField(max_length=64, unique=True, blank=True, null=True)
    students = models.ManyToManyField(Student, blank=True)
    

    def delete(self, *args, **kwargs):
        # Удалим файл перед удалением объекта
        if self.file and os.path.isfile(self.file.path):
            os.remove(self.file.path)
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.group_name}, {self.get_semester_display()} {self.academic_year})"

class Subject(models.Model):
    """Дисциплина."""
    name = models.CharField(max_length=255, unique=True)


class Grade(models.Model):
    vedomost = models.ForeignKey(  # Добавьте это поле
        Vedomost,
        on_delete=models.CASCADE,
        related_name='grades'
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    value = models.CharField(max_length=10)


class TeacherAssignmentFile(models.Model):
    file = models.FileField(upload_to='teacher_assignments/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Назначения от {self.uploaded_by.username} ({self.upload_date:%d.%m.%Y %H:%M})"


class TeachingAssignment(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    group = models.CharField(max_length=50)
    assignment_file = models.ForeignKey('TeacherAssignmentFile', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        profile = getattr(self.teacher, 'userprofile', None)
        if profile:
            name = f"{profile.last_name} {profile.first_name} {profile.middle_name}".strip()
        else:
            name = self.teacher.username
        return f"{name} — {self.subject.name} ({self.group})"

    class Meta:
        unique_together = ('teacher', 'subject', 'group')
