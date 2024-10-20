from django.db import models
from django.contrib.auth.models import AbstractUser, User
from .manager import UserManager
from phonenumber_field.modelfields import PhoneNumberField
from django_countries.fields import CountryField
# Create your models here.


class Department(models.Model):
    depart_name = models.CharField(max_length=255)
    def __str__(self) -> str:
        return self.depart_name
        
class Subject(models.Model):
    subject_code = models.CharField(max_length=255, null=True, blank=True)
    subject_name = models.CharField(max_length=255, null=True, blank=True)
    credit_hours = models.IntegerField(null=False, blank=False)
    subject_department = models.ForeignKey(Department, on_delete=models.CASCADE)
    def __str__(self) -> str:
        return str(self.subject_name)
    
class Semester(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    semester = models.CharField(max_length=20)
    
    def __str__(self) -> str:
        return str(self.semester)

class Country(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self) -> str:
        return str(self.name)
    
class Province(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    def __str__(self) -> str:
        return str(self.name)

class District(models.Model):
    name = models.CharField(max_length=100)
    province = models.ForeignKey(Province, on_delete=models.CASCADE)
    def __str__(self) -> str:
        return str(self.name)
class CustomUser(AbstractUser):
    username=None
    user_id = models.CharField(max_length=255, unique=True)
    profile_pic = models.ImageField(upload_to='images/', default='images/profile2.png')
    phone_number = models.CharField(max_length=11)
    objects = UserManager()
    USERNAME_FIELD = 'user_id'
    REQUIRED_FIELDS = []


    

class Teacher(CustomUser):
    is_sub_admin = models.BooleanField(null=True, blank=True, default=False)
    teacher_department = models.ForeignKey(Department, on_delete=models.CASCADE)
    teacher_name = models.CharField(max_length=255)
    def __str__(self) -> str:
        return str(self.teacher_name)
sess = [
    ('Fall', 'Fall'),
    ('Spring', 'Spring'),
]
student_gender = [
    ('Male', 'Male'),
    ('Female', 'Female'),
]
student_religion = [
    ('Islam', 'Islam'),
    ('Cristian', 'Cristian'),
    ('Hindu', 'Hindu'),
]
    
class Student(CustomUser):
    student_name = models.CharField(max_length=255, null=False, blank=False)
    father_name = models.CharField(max_length=255, null=False, blank=False)
    gender = models.CharField(max_length=255, choices=student_gender, null=False, blank=False)
    nationality = models.ForeignKey(Country, on_delete=models.CASCADE, null=False, blank=False)
    religion = models.CharField(max_length=255, choices=student_religion, null=False, blank=False)
    province = models.ForeignKey(Province, on_delete=models.CASCADE, null=False, blank=False)
    district = models.ForeignKey(District, on_delete=models.CASCADE, null=False, blank=False)
    dob = models.DateField(null=False, blank=False)
    cnic = models.CharField(max_length=13, unique=True, verbose_name='CNIC Number', null=False, blank=False)
    home_address = models.CharField(max_length=225, null=False, blank=False)
    mailing_address = models.CharField(max_length=225, null=False, blank=False)
    session = models.CharField(max_length=255, null=False, blank=False, choices=sess)
    addmission_year = models.DateField(null=False, blank=False)
    student_department = models.ForeignKey(Department, on_delete=models.CASCADE, null=False, blank=False)
    student_semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=False, blank=False)
    marks_visible = models.BooleanField(default=False)
    
    DisplayFields = ['user_id', 'profile_pic', 'student_name', 'session', 'addmission_year', 'phone_number', 'student_department', 'student_semester']
    def __str__(self) -> str:
        return str(self.student_name)



class SubjectAllocationModel(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    DisplayFields = ['teacher', 'student', 'subject', 'department']
    def __str__(self) -> str:
        return str(self.subject.subject_name)


class Assignment(models.Model):
    subject_allocation = models.CharField(max_length=255)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    marks = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    total_marks = models.DecimalField(max_digits=5, decimal_places=2)
    DisplayFields = ['subject_allocation', 'student', 'semester', 'title', 'marks', 'total_marks']


class Quiz(models.Model):
    subject_allocation = models.CharField(max_length=255)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    marks = models.DecimalField(max_digits=5, decimal_places=2)
    total_marks = models.DecimalField(max_digits=5, decimal_places=2)
    DisplayFields = ['subject_allocation', 'student', 'semester', 'title', 'marks', 'total_marks']


class Presentation(models.Model):
    subject_allocation = models.CharField(max_length=255)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    marks = models.DecimalField(max_digits=5, decimal_places=2)
    total_marks = models.DecimalField(max_digits=5, decimal_places=2)
    DisplayFields = ['subject_allocation', 'student', 'semester', 'title', 'marks', 'total_marks']


class Mid(models.Model):
    subject_allocation = models.CharField(max_length=255)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True, blank=True)
    marks = models.DecimalField(max_digits=5, decimal_places=2)
    total_marks = models.DecimalField(max_digits=5, decimal_places=2)
    DisplayFields = ['subject_allocation', 'student', 'semester', 'marks', 'total_marks']

    
class Final(models.Model):
    subject_allocation = models.CharField(max_length=255)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True, blank=True)
    marks = models.DecimalField(max_digits=5, decimal_places=2)
    total_marks = models.DecimalField(max_digits=5, decimal_places=2)
    DisplayFields = ['subject_allocation', 'student', 'semester', 'marks', 'total_marks']

class PaperResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject_allocation = models.CharField(max_length=255)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True, blank=True)
    gp = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    qp = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    marks = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    total_marks = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    grade = models.CharField(max_length=2, null=True, blank=True)
    credit_hours = models.IntegerField(null=True, blank=True)
    def __str__(self) -> str:
        return str(self.student)
    
class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True, blank=True)
    marks = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    total_marks = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    t_qp = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    t_credit_hours = models.IntegerField(null=True, blank=True)
    gpa = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    

    def __str__(self) -> str:
        return str(self.student)
    
class Attendence(models.Model):
    attendence_department = models.CharField(max_length=255, null=True, blank=True)
    attendence_semester = models.CharField(max_length=255, null=True, blank=True)
    attendence_subject = models.CharField(max_length=255, null=True, blank=True)
    attendence_date = models.DateField()
    def __str__(self):
        return f'{self.attendence_subject}'
    
    
class AttendenceReport(models.Model):
    attendence_student = models.ForeignKey(Student,  null=True, blank=True, on_delete=models.CASCADE)
    attendence_id = models.ForeignKey(Attendence,  null=True, blank=True,on_delete=models.CASCADE)
    attendence_status = models.CharField(max_length=10)
    def __str__(self) -> str:
        return f'{self.attendence_student} / {self.attendence_status}'


