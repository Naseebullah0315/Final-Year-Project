from typing import Any, Dict
from django import forms
from accounts.models import *



class DepartmentAddForm(forms.ModelForm):

    class Meta:
        model = Department
        fields = ['depart_name']
        widgets = {
            'depart_name': forms.TextInput(attrs={'class':'form-control'}),
        }
    def clean_depart_name(self):
        department = self.cleaned_data['depart_name']
        if department:
            if Department.objects.filter(depart_name=department).exists():
                raise forms.ValidationError(f'{department} is Already Added')
            return department


class ProfilePicChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['profile_pic']
        widgets = {
            'profile_pic' : forms.ClearableFileInput(attrs={'class':'form-control'}),
        }

        
class SemesterAddForm(forms.ModelForm):

    class Meta:
        model = Semester
        fields = ['semester']
        widgets = {
            'semester': forms.TextInput(attrs={'class':'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        self.department = kwargs.pop('department', None)
        super().__init__(*args, **kwargs)
    def clean_semester(self):
        semester = self.cleaned_data['semester']
        if Semester.objects.filter(semester=semester, department=self.department).exists():  
            raise forms.ValidationError(f'{semester} is Already Added')
        semesters = ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', 'Graduate']
        if semester not in semesters: 
                raise forms.ValidationError("Invalid semester. Please choose from: '1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', 'Graduate'.")
        return semester


class DepartmentUpdateForm(forms.ModelForm):

    class Meta:
        model = Department
        fields = ['depart_name']
        widgets = {
            'depart_name': forms.TextInput(attrs={'class':'form-control'}),
        }
    def clean_depart_name(self):
        department = self.cleaned_data['depart_name']
        if department:
            if Department.objects.filter(depart_name=department).exists():
                raise forms.ValidationError(f'{department} is Already Added')
            return department



class StudentUpdateForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['user_id', 'student_name', 'student_department', 'student_semester', 'session', 'addmission_year', 'marks_visible']
        widgets = {
            'user_id': forms.TextInput(attrs={'class':'form-control'}),
            'student_name': forms.TextInput(attrs={'class':'form-control'}),
            'student_department': forms.Select(attrs={'class':'form-control'}),
            'student_semester': forms.Select(attrs={'class':'form-control'}),
            'session': forms.Select(attrs={'class':'form-control'}),
            'addmission_year': forms.DateInput(attrs={'class':'form-control', 'type':'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student_semester'].queryset = Semester.objects.none()
        if 'student_department' in self.data:
            try:
                department_id = int(self.data.get('student_department'))
                self.fields['student_semester'].queryset = Semester.objects.filter(department_id=department_id)
            except(ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['student_semester'].queryset = self.instance.student_department.semester_set.order_by('semester')
 

class SemesterUpdateForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['student_semester']
        widgets = {
            'student_semester': forms.Select(attrs={'class':'form-control'}),
        }    



class SubjectCreateForm(forms.ModelForm):

    class Meta:
        model = Subject
        fields = ['subject_code', 'subject_name', 'credit_hours']
        widgets = {
            'subject_code': forms.TextInput(attrs={'class':'form-control'}),
            'subject_name': forms.TextInput(attrs={'class':'form-control'}),
            'credit_hours': forms.NumberInput(attrs={'class':'form-control'}),
        }
    def clean_subject_name(self):
        subject_name = self.cleaned_data.get('subject_name')
        if subject_name:
            if Subject.objects.filter(subject_name=subject_name).exists():
                raise forms.ValidationError(f'{subject_name} Subject is Already Added')
        return subject_name

    def clean_subject_code(self):
        subject_code = self.cleaned_data.get('subject_code')
        if subject_code:
            if Subject.objects.filter(subject_code=subject_code).exists():
                raise forms.ValidationError(f'{subject_code} Subject Code is Already Aloted to the Subject')
        return subject_code

    def clean_credit_hours(self):
        credit_hours = self.cleaned_data.get('credit_hours')
        if credit_hours > 5:
            raise forms.ValidationError(f'The Credit hours can be maximum 5 hours')
        return credit_hours


class SubjectUpdateForm(forms.ModelForm):

    class Meta:
        model = Subject
        fields = ['subject_code', 'subject_name', 'credit_hours']
        widgets = {
            'subject_code': forms.TextInput(attrs={'class':'form-control'}),
            'subject_name': forms.TextInput(attrs={'class':'form-control'}),
            'credit_hours': forms.TextInput(attrs={'class':'form-control'}),
        }
    

class AdminSubjectAllocationForm(forms.ModelForm):

    class Meta:
        model = SubjectAllocationModel
        fields = ['subject', 'teacher', 'semester']
        widgets = {
            'subject': forms.Select(attrs={'class':'form-control'}),
            'teacher': forms.Select(attrs={'class':'form-control'}),
            'semester': forms.Select(attrs={'class':'form-control'}),
        }

        
    def clean(self):
        cleaned_data = super().clean()
        subject = cleaned_data.get('subject')
        semester = cleaned_data.get('semester')
        teacher = cleaned_data.get('teacher')

        if subject and semester and teacher:
            existing_allocation_t = SubjectAllocationModel.objects.filter(
                subject=subject,
                semester=semester,
                teacher=teacher
            ).exists()
            if existing_allocation_t:
                raise forms.ValidationError('Teacher has already allocated the same subject to the same semester')
        if subject and semester:
            existing_allocation = SubjectAllocationModel.objects.filter(
                subject = subject,
                semester = semester
            )
        
            if existing_allocation:
                raise forms.ValidationError('The Subject is Already Allocated to the same Semester')
        return cleaned_data
class SubjectAllocationForm(forms.ModelForm):

    class Meta:
        model = SubjectAllocationModel
        fields = ['subject', 'teacher', 'semester']
        widgets = {
            'subject': forms.Select(attrs={'class':'form-control'}),
            'teacher': forms.Select(attrs={'class':'form-control'}),
            'semester': forms.Select(attrs={'class':'form-control'}),
        }
    def clean(self):
        cleaned_data = super().clean()
        subject = cleaned_data.get('subject')
        semester = cleaned_data.get('semester')
        teacher = cleaned_data.get('teacher')

        if subject and semester and teacher:
            existing_allocation_t = SubjectAllocationModel.objects.filter(
                subject=subject,
                semester=semester,
                teacher=teacher
            ).exists()
            if existing_allocation_t:
                raise forms.ValidationError('Teacher has already allocated the same subject to the same semester')
        if subject and semester:
            existing_allocation = SubjectAllocationModel.objects.filter(
                subject = subject,
                semester = semester,
            ).exists()
        
            if existing_allocation:
                raise forms.ValidationError('The Subject is Already Allocated to the same Semester')
        return cleaned_data

class SubjectAllocationUpdateForm(forms.ModelForm):

    class Meta:
        model = SubjectAllocationModel
        fields = ['subject', 'teacher', 'semester']
        widgets = {
            'subject': forms.Select(attrs={'class':'form-control'}),
            'teacher': forms.Select(attrs={'class':'form-control'}),
            'semester': forms.Select(attrs={'class':'form-control'}),
        }
    
    
class AttendenceReportForm(forms.ModelForm):
    class Meta:
        model = AttendenceReport
        fields = ['attendence_student', 'attendence_status']

        widgets = {
            'attendence_student' : forms.Select(attrs={'class':'form-control'}),
        }
        
class AttendenceDateUpdateForm(forms.ModelForm):
    class Meta:
        model = Attendence
        fields = ['attendence_date']

        widgets = {
            'attendence_date' : forms.DateInput(attrs={'class':'form-control', 'type':'date'}),
        }

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'marks', 'total_marks']
        widgets = {
            'title' : forms.TextInput(attrs={'class':'form-control'}),
            'marks' : forms.NumberInput(attrs={'class':'form-control'}),
            'total_marks' : forms.NumberInput(attrs={'class':'form-control'}),
        }
        
class AssignmentUpdateForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'marks', 'total_marks']
        widgets = {
            'title' : forms.TextInput(attrs={'class':'form-control'}),
            'marks' : forms.NumberInput(attrs={'class':'form-control'}),
            'total_marks' : forms.NumberInput(attrs={'class':'form-control'}),
        }

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'marks', 'total_marks']
        widgets = {
            'title' : forms.TextInput(attrs={'class':'form-control'}),
            'marks' : forms.NumberInput(attrs={'class':'form-control'}),
            'total_marks' : forms.NumberInput(attrs={'class':'form-control'}),
        }

class QuizUpdateForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'marks', 'total_marks']
        widgets = {
            'title' : forms.TextInput(attrs={'class':'form-control'}),
            'marks' : forms.NumberInput(attrs={'class':'form-control'}),
            'total_marks' : forms.NumberInput(attrs={'class':'form-control'}),
        }

class PresentationForm(forms.ModelForm):
    class Meta:
        model = Presentation
        fields = ['title', 'marks', 'total_marks']
        widgets = {
            'title' : forms.TextInput(attrs={'class':'form-control'}),
            'marks' : forms.NumberInput(attrs={'class':'form-control'}),
            'total_marks' : forms.NumberInput(attrs={'class':'form-control'}),
        }

class PresentationUpdateForm(forms.ModelForm):
    class Meta:
        model = Presentation
        fields = ['title', 'marks', 'total_marks']
        widgets = {
            'title' : forms.TextInput(attrs={'class':'form-control'}),
            'marks' : forms.NumberInput(attrs={'class':'form-control'}),
            'total_marks' : forms.NumberInput(attrs={'class':'form-control'}),
        }

class MidForm(forms.ModelForm):
    class Meta:
        model = Mid
        fields = ['marks', 'total_marks']
        widgets = {
            'marks' : forms.NumberInput(attrs={'class':'form-control'}),
            'total_marks' : forms.NumberInput(attrs={'class':'form-control'}),
        }

class MidUpdateForm(forms.ModelForm):
    class Meta:
        model = Mid
        fields = ['marks', 'total_marks']
        widgets = {
            'marks' : forms.NumberInput(attrs={'class':'form-control'}),
            'total_marks' : forms.NumberInput(attrs={'class':'form-control'}),
        }

class FinalForm(forms.ModelForm):
    class Meta:
        model = Final
        fields = ['marks', 'total_marks']
        widgets = {
            'marks' : forms.NumberInput(attrs={'class':'form-control'}),
            'total_marks' : forms.NumberInput(attrs={'class':'form-control'}),
        }

class FinalUpdateForm(forms.ModelForm):
    class Meta:
        model = Final
        fields = ['marks', 'total_marks']
        widgets = {
            'marks' : forms.NumberInput(attrs={'class':'form-control'}),
            'total_marks' : forms.NumberInput(attrs={'class':'form-control'}),
        }
        