from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

class UploadFileForm(forms.Form):
    """Форма загрузки файла."""
    file = forms.FileField(label="Выберите Excel-файл")

    def clean_file(self):
        file = self.cleaned_data['file']
        if not file.name.endswith(('.xlsx', '.xls')):
            raise forms.ValidationError("Можно загружать только Excel-файлы (.xlsx или .xls)")
        return file

class CreateTeacherForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']  # Только User-поля
        labels = {
            'username': 'Логин',
            'email': 'Email',
        }

    # ФИО добавляем отдельно в __init__ и обрабатываем вручную
    first_name = forms.CharField(label="Имя", max_length=150)
    last_name = forms.CharField(label="Фамилия", max_length=150)
    middle_name = forms.CharField(label="Отчество", max_length=150, required=False)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()

            # Явно создаем профиль с ФИО
            UserProfile.objects.create(
                user=user,
                role='teacher',
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                middle_name=self.cleaned_data['middle_name']
            )

        return user


class ReportGenerationForm(forms.Form):
    REPORT_TYPE_CHOICES = [
        ('group', 'По группе'),
        ('student', 'По студенту'),
        ('teacher', 'По преподавателю'),
    ]

    report_type = forms.ChoiceField(choices=REPORT_TYPE_CHOICES, label="Тип отчёта")

    group = forms.ChoiceField(required=False, label="Группа")
    student = forms.ChoiceField(required=False, label="Студент")
    from_year = forms.ChoiceField(label="С учебного года")
    to_year = forms.ChoiceField(label="По учебный год")
    teacher = forms.ChoiceField(required=False, label="Преподаватель")


    def __init__(self, *args, **kwargs):
        groups = kwargs.pop('groups', [])
        years = kwargs.pop('years', [])
        students = kwargs.pop('students', [])
        teachers = kwargs.pop('teachers', [])
        super().__init__(*args, **kwargs)

        self.fields['group'].choices = [('', 'Выберите')] + [(g, g) for g in groups]
        self.fields['student'].choices = [('', 'Выберите')] + [(s.id, s.full_name) for s in students]
        self.fields['from_year'].choices = [(y, y) for y in years]
        self.fields['to_year'].choices = [(y, y) for y in years]
        self.fields['teacher'].choices = [('', 'Выберите')] + [(u.id, f"{u.userprofile.last_name} {u.userprofile.first_name}") for u in teachers]

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('from_year') and cleaned.get('to_year'):
            if cleaned['from_year'] > cleaned['to_year']:
                raise forms.ValidationError("Год 'по' не может быть раньше 'с'.")


class EditUserForm(forms.ModelForm):
    first_name = forms.CharField(label="Имя", max_length=150)
    last_name = forms.CharField(label="Фамилия", max_length=150)
    middle_name = forms.CharField(label="Отчество", max_length=150, required=False)
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES, label="Роль")

    class Meta:
        model = User
        fields = ['username', 'email']


class VedomostFilterForm(forms.Form):
    group = forms.ChoiceField(required=False, label="Группа")
    academic_year = forms.ChoiceField(required=False, label="Учебный год")
    uploaded_by = forms.ChoiceField(required=False, label="Преподаватель")

    def __init__(self, *args, **kwargs):
        vedomosti = kwargs.pop('vedomosti')
        super().__init__(*args, **kwargs)

        # Уникальные группы
        groups = sorted(set(vedomosti.values_list('group_name', flat=True).distinct()))
        self.fields['group'].choices = [('', 'Все')] + [(g, g) for g in groups if g]

        # Уникальные учебные годы
        years = sorted(set(vedomosti.values_list('academic_year', flat=True).distinct()))
        self.fields['academic_year'].choices = [('', 'Все')] + [(y, y) for y in years if y]

        # Преподаватели по ФИО
        teacher_ids = vedomosti.values_list('uploaded_by', flat=True).distinct()
        teachers = UserProfile.objects.filter(user__id__in=teacher_ids, role='teacher')
        teacher_choices = [('', 'Все')] + [
            (t.user.id, f"{t.last_name} {t.first_name} {t.middle_name}".strip()) for t in teachers
        ]
        self.fields['uploaded_by'].choices = teacher_choices
