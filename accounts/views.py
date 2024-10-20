from django.contrib.auth.forms import AuthenticationForm
from django.forms.models import BaseModelForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.views import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import *
from .forms import *
from django.contrib.auth import authenticate, login, update_session_auth_hash, logout
from django.urls import reverse
from .models import*
from django.urls import reverse_lazy
from .mixins import *
from uniapp.mixins import *
from django.contrib import messages

# Create your views here.
def custom_logout(request):
    logout(request)
    # Redirect to the login page or any other page after logout
    return redirect('login')


@login_not_required
def login_view(request):
    msg = None
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if not (username and password):
            error_message = "Please provide both User ID and password."
            return render(request, 'register/login.html', {'error_message': error_message})
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'You have Logged In Successfully')
            if user.is_superuser:
                return redirect('uniapp:admin_dashboard')
            elif hasattr(user, 'student'):
                return redirect('uniapp:student_dashboard')
            elif hasattr(user, 'teacher') and not user.teacher.is_sub_admin:
                return redirect('uniapp:teacher')
            elif hasattr(user, 'teacher') and user.teacher.is_sub_admin:
                return redirect('uniapp:teacher_admin_dashboard')
        else:
            error_message = 'User Id or Password is Wrong'
            return render(request, 'register/login.html', {'error_message': error_message})
    return render(request, 'register/login.html')

class TeacherAdminSignupView(SubAdminRequiredMixin ,CreateView):
    form_class = TeacherHODSignUpForm
    template_name = 'register/teacher_admin_signup.html'
    success_url = reverse_lazy('uniapp:teacher_admin_dashboard')
    def form_valid(self, form):
        form.instance.teacher_department = self.request.user.teacher.teacher_department
        if form.instance.is_sub_admin == True:
            messages.success(self.request, 'The HOD is Added Successully')
        else:
            messages.success(self.request, 'The Teacher is Added Successully')
        return super().form_valid(form)
    # def form_invalid(self, form):
    #     messages.error(self.request, f'There is an error within the form')
    #     return super().form_invalid(form)

class AdminSignupView(AdminRequiredMixin, CreateView):
    form_class = TeacherAdminSignUpForm
    template_name = 'register/signup.html'
    success_url = reverse_lazy('uniapp:admin_dashboard')
    def form_valid(self, form):
        if form.instance.is_sub_admin == True:
            messages.success(self.request, 'The HOD is Added Successully')
        else:
            messages.success(self.request, 'The Teacher is Added Successully')
        return super().form_valid(form)
    


class UserPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    form_class = PasswordChangeForm
    template_name = 'register/passwordchange.html'
    success_url = reverse_lazy('uniapp:profile')


#For Updating the Teacher Added By the Department HOD
class TeacherUpdateView(All_Except_Student_Mixin, UpdateView):
    model = Teacher
    form_class = TeacherAdminSignUpUpdateForm
    template_name = 'register/teacherupdate.html'
    def get_success_url(self):
        messages.success(self.request, f'The Teacher is Updated Successully')
        if self.request.user.is_superuser:
            return reverse_lazy('uniapp:departments')
        elif self.request.user.teacher.is_sub_admin:
            return reverse_lazy('uniapp:teacherlist')