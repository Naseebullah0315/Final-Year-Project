from django.urls import reverse
from django.shortcuts import redirect

class RoleRestrictionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # if request.user.is_authenticated:
        #     if request.user.is_admin and 'teacher_dashboard' in request.path:
        #         return redirect(reverse('admin_dashboard'))
        #     elif request.user.is_admin and 'student_dashboard' in request.path:
        #         return redirect(reverse('admin_dashboard'))
        #     elif request.user.is_teacher and 'student_dashboard' in request.path:
        #         return redirect(reverse('teacher_dashboard'))
        #     elif request.user.is_teacher and 'admin_dashboard' in request.path:
        #         return redirect(reverse('teacher_dashboard'))
        #     elif request.user.is_student and 'teacher' in request.path:
        #         return redirect(reverse('student_dashboard'))
        #     elif request.user.is_student and 'admin_dashboard' in request.path:
        #         return redirect(reverse('student_dashboard'))

        return self.get_response(request)