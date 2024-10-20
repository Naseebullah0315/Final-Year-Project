from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from accounts.models import*
from django.contrib import messages
from django.http import HttpResponseForbidden
from functools import wraps
from accounts.models import *

def login_not_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            if hasattr(request.user, 'teacher') and request.user.teacher.is_sub_admin:
                return redirect('uniapp:teacher_admin_dashboard')
            elif hasattr(request.user, 'teacher') and not request.user.teacher.is_sub_admin:
                return redirect('uniapp:teacher')
            elif request.user.is_superuser:
                return redirect('uniapp:admin_dashboard')
            elif hasattr(request.user, 'student'):
                return redirect('uniapp:student_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper

class AdminRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            if not request.user.is_authenticated:
                return redirect('login')
            else:
                return HttpResponseForbidden('You are not allow to access this page')
            
        return super().dispatch(request, *args, **kwargs)
    
class SubAdminRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs): 
        if request.user.is_authenticated:
            hod_check = self.request.session.get('show_allocated_subjects')
            if hasattr(request.user, 'teacher') and request.user.teacher.is_sub_admin and not hod_check:
                return super().dispatch(request, *args, **kwargs)
            if hasattr(request.user, 'teacher') and request.user.teacher.is_sub_admin and hod_check:
                return HttpResponseForbidden('You are not allowed to access this page right now. Please Switch to HOD')
            else:
                return HttpResponseForbidden('You are not allowed to access this page.')
        else:
            return redirect('login')
    
class TeacherRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'teacher'):
            if not request.user.is_authenticated:
                return redirect('login')
            else:
                return HttpResponseForbidden('You are not allow to access this page')
        return super().dispatch(request, *args, **kwargs)

class TeacherRequiredMarksMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            subject_id = self.kwargs['subjectallocationmodel_id']

            student_id = self.request.session.get('student_id')
            # subject_id = self.request.session.get('subject_id')
            print(f'The subject ID is: {student_id}/{subject_id}')
            student = Student.objects.get(id=student_id)
            subject = SubjectAllocationModel.objects.get(id=subject_id)
            print(f'The subject ID is: {subject_id}/{student_id}')
            marks = student.marks_visible
            if hasattr(request.user, 'teacher') and not marks and subject.teacher == self.request.user.teacher or self.request.user.is_superuser:
                return super().dispatch(request, *args, **kwargs)
            else:
                return HttpResponseForbidden('You are not allow to access this page')
        else:
            return redirect('login')

class AssessementUpdateMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            student_id = self.request.session.get('student_id')
            # subject_id = self.kwargs['subjectallocationmodel_id']
            subject_id = self.request.session.get('subject_id')
            subject = SubjectAllocationModel.objects.get(id=subject_id)
            student = Student.objects.get(id=student_id)
            marks = student.marks_visible
            if hasattr(request.user, 'teacher') and not marks or request.user.is_superuser :
                return super().dispatch(request, *args, **kwargs)
            else:
                return HttpResponseForbidden('You are not allow to access this page')
        else:
            return redirect('login')

class HOD_And_Teacher_Required_Mixin(AccessMixin):
    def dispatch(self, request,*args, **kwargs):
        if not request.user.is_authenticated:
                return redirect('login')
        if request.user.teacher:
            if request.user.is_superuser:
                return HttpResponseForbidden('You are not allow to access this page')
        return super().dispatch(request, *args, **kwargs)

class Student_Required_Mixin(AccessMixin):
    def dispatch(self, request,*args, **kwargs):
        if not hasattr(request.user, 'student'):
            if not request.user.is_authenticated:
                return redirect('login')
            else:
                return HttpResponseForbidden('You are not allow to access this page')
        return super().dispatch(request, *args, **kwargs)


class All_Except_Student_Mixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs): 
        if request.user.is_authenticated:
            if hasattr(request.user, 'teacher') or request.user.is_superuser:
                return super().dispatch(request, *args, **kwargs)
            else:
                return HttpResponseForbidden('You are not allowed to access this page.')
        else:
            return redirect('login')
            
class Admin_And_HOD_Required_Mixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs): 
        if request.user.is_authenticated:
            hod_check = self.request.session.get('show_allocated_subjects')
            if hasattr(request.user, 'teacher') and request.user.teacher.is_sub_admin and not hod_check or request.user.is_superuser:
                return super().dispatch(request, *args, **kwargs)
            else:
                return HttpResponseForbidden('You are not allowed to access this page.')
        else:
            return redirect('login')
            

    