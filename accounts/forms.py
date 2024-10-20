from typing import Any
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm,  PasswordChangeForm
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import authenticate
from phonenumber_field.modelfields import PhoneNumberField

            


class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'password']
class AdminSignUpForm(UserCreationForm):
    
    class Meta:
        model = CustomUser
        fields = ['email','phone_number', 'password1', 'password2']
        widgets = {
        'email': forms.EmailInput(attrs={'class':'form-control'}),            
        'phone_number' : forms.TextInput(attrs={'class':'form-control'}),
        'password1' : forms.PasswordInput(attrs={'class':'form-control'}),
        'password2' : forms.PasswordInput(attrs={'class':'form-control'}),
        }
class TeacherAdminSignUpForm(UserCreationForm):
    class Meta:
        model = Teacher
        fields = ['user_id', 'teacher_name', 'teacher_department','email', 'profile_pic', 'phone_number', 'is_sub_admin', 'password1', 'password2']
        widgets = {
            'user_id' : forms.TextInput(attrs={'class':'form-control'}),
            'teacher_name' : forms.TextInput(attrs={'class':'form-control'}),
            'teacher_department' : forms.Select(attrs={'class':'form-control'}),
            'email': forms.EmailInput(attrs={'class':'form-control'}),
            'profile_pic' : forms.ClearableFileInput(attrs={'class':'form-control'}),
            'phone_number' : forms.NumberInput(attrs={'class':'form-control'}),
            'is_sub_admin' : forms.NullBooleanSelect(attrs={'class':'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
    def clean_user_id(self):
        user_id = self.cleaned_data['user_id']
        if user_id and len(user_id) < 3:
            raise forms.ValidationError('The User Id Must Be Greater Than 3 Charectors')
        
        elif user_id:
            if Teacher.objects.filter(user_id=user_id).exists():
                raise forms.ValidationError(f'The Teacher with {user_id} user id Already Exist')
            
        return user_id
    def clean_email(self):
        email = self.cleaned_data['email']
        if email:
            if Student.objects.filter(email=email).exists():
                raise forms.ValidationError(f'This email address is already used')
        return email

class TeacherHODSignUpForm(UserCreationForm):
    class Meta:
        model = Teacher
        fields = ['user_id', 'teacher_name','email', 'profile_pic', 'phone_number', 'is_sub_admin', 'password1', 'password2']
        widgets = {
            'user_id' : forms.TextInput(attrs={'class':'form-control'}),
            'teacher_name' : forms.TextInput(attrs={'class':'form-control'}),
            'email': forms.EmailInput(attrs={'class':'form-control'}),
            'profile_pic' : forms.ClearableFileInput(attrs={'class':'form-control'}),
            'phone_number' : forms.NumberInput(attrs={'class':'form-control'}),
            'is_sub_admin' : forms.NullBooleanSelect(attrs={'class':'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
    def clean_user_id(self):
        user_id = self.cleaned_data['user_id']
        if user_id and len(user_id) < 3:
            raise forms.ValidationError('The User Id Must Be Greater Than 3 Charectors')
        
        elif user_id:
            if Teacher.objects.filter(user_id=user_id).exists():
                raise forms.ValidationError(f'The Teacher with {user_id} user id Already Exist')
            
        return user_id
    def clean_email(self):
        email = self.cleaned_data['email']
        if email:
            if Student.objects.filter(email=email).exists():
                raise forms.ValidationError(f'This email address is already used')
        return email

class AllStudentCreateForm(UserCreationForm):
    # student_semester = forms.ModelChoiceField(
    #     queryset=Semester.objects.order_by('semester'),  # Ordering semesters by name
    #     widget=forms.Select(attrs={'class':'form-control'}),
    #     empty_label="Select Semester")  # Optional: to add a placeholder
    class Meta:
        model = Student
        fields = ['user_id', 'student_name', 'father_name', 'gender', 'student_semester', 'cnic', 'nationality', 'province', 'district', 'home_address', 'mailing_address', 'religion', 'dob', 'email','session', 'addmission_year', 'profile_pic', 'phone_number', 'password1', 'password2']
        

        widgets = {
            'user_id': forms.TextInput(attrs={'class':'form-control'}),
            'student_name': forms.TextInput(attrs={'class':'form-control'}),
            'student_semester': forms.Select(attrs={'class':'form-control'}),
            'father_name': forms.TextInput(attrs={'class':'form-control'}),
            'gender': forms.Select(attrs={'class':'form-control'}),
            'cnic': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Enter the CNIC number without dashes'}, ),
            'nationality': forms.Select(attrs={'class':'form-control'}),
            'province': forms.Select(attrs={'class':'form-control'}),
            'district': forms.Select(attrs={'class':'form-control'}),
            'home_address': forms.TextInput(attrs={'class':'form-control'}),
            'mailing_address': forms.TextInput(attrs={'class':'form-control'}),
            'religion': forms.Select(attrs={'class':'form-control'}),
            'dob': forms.DateInput(attrs={'class':'form-control', 'type':'date'}),
            'nationality': forms.Select(attrs={'class':'form-control'}),
            'email': forms.EmailInput(attrs={'class':'form-control'}),
            'session': forms.Select(attrs={'class':'form-control'}),
            'addmission_year': forms.DateInput(attrs={'class':'form-control', 'type':'date'}),
            'profile_pic': forms.ClearableFileInput(attrs={'class':'form-control'}),
            'phone_number' : forms.TextInput(attrs={'class':'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['province'].queryset = Province.objects.none()
        self.fields['district'].queryset = District.objects.none()
        
        
        if 'nationality' in self.data:
            try:
                country_id = int(self.data.get('nationality'))
                self.fields['province'].queryset = Province.objects.filter(country_id=country_id).order_by('name')
            except(ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['province'].queryset = self.instance.nationality.province_set.order_by('province')
        if 'province' in self.data:
            try:
                province_id = int(self.data.get('province'))
                self.fields['district'].queryset = District.objects.filter(province_id=province_id).order_by('name')
            except(ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['district'].queryset = self.instance.province.district_set.order_by('district')
    

    
            
    def clean_user_id(self):
        user_id = self.cleaned_data['user_id']
        if user_id:
            if Student.objects.filter(user_id=user_id).exists():
                raise forms.ValidationError(f'A student with {user_id} user id already exists')
        return user_id

    def clean_email(self):
        email = self.cleaned_data['email']
        if email:
            if Student.objects.filter(email=email).exists():
                raise forms.ValidationError(f'This email address is already used')
        return email

    def clean_addmission_year(self):
        addmission_year = self.cleaned_data['addmission_year']
        if not addmission_year:
            raise forms.ValidationError(f'Enter the Addmission Year')
        return addmission_year


class SemesterStudentCreateForm(UserCreationForm):

    class Meta:
        model = Student
        fields = ['user_id', 'student_name', 'father_name', 'gender', 'cnic', 'nationality', 'province', 'district', 'home_address', 'mailing_address', 'religion', 'dob', 'email','session', 'addmission_year', 'profile_pic', 'phone_number', 'password1', 'password2']

        widgets = {
            'user_id': forms.TextInput(attrs={'class':'form-control'}),
            'student_name': forms.TextInput(attrs={'class':'form-control'}),
            'father_name': forms.TextInput(attrs={'class':'form-control'}),
            'gender': forms.Select(attrs={'class':'form-control'}),
            'cnic': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Enter the CNIC number without dashes'}, ),
            'nationality': forms.Select(attrs={'class':'form-control'}),
            'province': forms.Select(attrs={'class':'form-control'}),
            'district': forms.Select(attrs={'class':'form-control'}),
            'home_address': forms.TextInput(attrs={'class':'form-control'}),
            'mailing_address': forms.TextInput(attrs={'class':'form-control'}),
            'religion': forms.Select(attrs={'class':'form-control'}),
            'dob': forms.DateInput(attrs={'class':'form-control', 'type':'date'}),
            'nationality': forms.Select(attrs={'class':'form-control'}),
            'email': forms.EmailInput(attrs={'class':'form-control'}),
            'session': forms.Select(attrs={'class':'form-control'}),
            'addmission_year': forms.DateInput(attrs={'class':'form-control', 'type':'date'}),
            'profile_pic': forms.ClearableFileInput(attrs={'class':'form-control'}),
            'phone_number' : forms.TextInput(attrs={'class':'form-control'}),
        }
  

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['province'].queryset = Province.objects.none()
        self.fields['district'].queryset = District.objects.none()

        if 'nationality' in self.data:
            try:
                country_id = int(self.data.get('nationality'))
                self.fields['province'].queryset = Province.objects.filter(country_id=country_id).order_by('name')
            except(ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['province'].queryset = self.instance.nationality.province_set.order_by('province')
        if 'province' in self.data:
            try:
                province_id = int(self.data.get('province'))
                self.fields['district'].queryset = District.objects.filter(province_id=province_id).order_by('name')
            except(ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['district'].queryset = self.instance.province.district_set.order_by('district')
 
    
   
    def clean_user_id(self):
        user_id = self.cleaned_data['user_id']
        if user_id and len(user_id) < 3:
            raise forms.ValidationError('The User Id Must Be Greater Than 3 Charectors')
        
        elif user_id:
            if Student.objects.filter(user_id=user_id).exists():
                raise forms.ValidationError(f'A student with {user_id} user id already exists')
        return user_id

    def clean_email(self):
        email = self.cleaned_data['email']
        if email:
            if Student.objects.filter(email=email).exists():
                raise forms.ValidationError(f'This email address is already used')
        return email
    def clean_cnic(self):
        cnic = self.cleaned_data['cnic']
        valid_numbers = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}
        if any(char not in valid_numbers for char in cnic):
            raise forms.ValidationError('Please enter a valid CNIC with only numbers.')
        
        elif len(cnic) < 13:
            raise forms.ValidationError('CNIC must be at least 13 digits long.')
            
        elif Student.objects.filter(cnic=cnic).exists():
            raise forms.ValidationError('This CNIC is already added')
        
        return cnic

    def clean_addmission_year(self):
        addmission_year = self.cleaned_data['addmission_year']
        if not addmission_year:
            raise forms.ValidationError(f'Enter the Addmission Year')
        return addmission_year

class TeacherAdminSignUpUpdateForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['user_id', 'teacher_name', 'email','phone_number', 'is_sub_admin']
        widgets = {
            'user_id' : forms.TextInput(attrs={'class':'form-control'}),
            'teacher_name' : forms.TextInput(attrs={'class':'form-control'}),
            'email' : forms.EmailInput(attrs={'class':'form-control'}),
            'profile_pic' : forms.ClearableFileInput(attrs={'class':'form-control'}),
            'phone_number' : forms.NumberInput(attrs={'class':'form-control'}),
            'is_sub_admin' : forms.NullBooleanSelect(attrs={'class':'form-control'}),
        }
    # def clean_user_id(self):
    #     user_id = self.cleaned_data.get('user_id')
    #     if user_id:
    #         if Teacher.objects.filter(user_id=user_id).exists():
    #             raise forms.ValidationError(f'The Teacher with {user_id} user id Already Exist')
    #     return user_id
    # def clean_email(self):
    #     email = self.cleaned_data['email']
    #     if email:
    #         if Student.objects.filter(email=email).exists():
    #             raise forms.ValidationError(f'This email address is already used')
    #     return email

        
    
class PasswordChangeForm(PasswordChangeForm):
    class Mete:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs['class'] = 'form-control'
        self.fields['new_password1'].widget.attrs['class'] = 'form-control'
        self.fields['new_password2'].widget.attrs['class'] = 'form-control'
    
