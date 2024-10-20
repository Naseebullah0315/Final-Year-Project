from functools import wraps
from django.shortcuts import redirect

# def login_not_required(view_func):
#     @wraps(view_func)
#     def wrapper(request, *args, **kwargs):
#         if request.user.is_authenticated:
#             if request.user.is_sub_admin:
#                 return redirect('uniapp:teacher_admin_dashboard')
#             elif request.user.is_sub_admin==False and request.user.is_superuser==False:
#                 return redirect('uniapp:teacher')
#             elif request.user.teacher.is_superuser:
#                 return redirect('uniapp:admin_dashboard')
#         return view_func(request, *args, **kwargs)
#     return wrapper
