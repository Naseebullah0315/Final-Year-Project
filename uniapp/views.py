from datetime import date
from typing import Any, Dict, Optional, Type
from django.forms.models import BaseModelForm
from django.http import HttpResponse, FileResponse, JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.views.generic import *
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.forms import *
from django.urls import reverse_lazy, reverse
from .models import *
from .forms import *
from django.db.models import Q
from .mixins import *
from django.contrib import messages
from django.db.models import Sum
from django.http import JsonResponse
import io
from io import BytesIO
from reportlab.lib.utils import ImageReader
from decimal import Decimal, InvalidOperation

from .filters import *
from django.template.loader import get_template

# Imports For Generating PDF
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, inch, letter
from reportlab.lib import colors
from reportlab.lib.colors import rgb2cmyk
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfgen import canvas


#Profile of the logged in User(i.e Admin, HOD, Teacher, Student)
class Profile(LoginRequiredMixin, TemplateView):
    template_name = 'profile.html'

class ProfilePicChangeView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    template_name = 'ProfilePicChange.html'
    form_class = ProfilePicChangeForm
    success_url = reverse_lazy('uniapp:profile')
    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Profile picture updated successfully.')
        return super().form_valid(form)




#This is the Dashboard for the HOD of the respective department
class Teacher_Admin_Dashboard(SubAdminRequiredMixin, TemplateView):
    template_name = 'teacher_admin_dashboard.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher_department = self.request.user.teacher.teacher_department
        teacher_count = Teacher.objects.filter(teacher_department=teacher_department).count()
        student_count = Student.objects.filter(student_department=teacher_department).count()
        subject_count = Subject.objects.filter(subject_department=teacher_department).count()

        context['teacher_count'] = teacher_count
        context['student_count'] = student_count
        context['subject_count'] = subject_count
        return context
    

#This is the Staff Teacher Dashboard  
class TeacherAsUserView(TeacherRequiredMixin, TemplateView):
    template_name = 'teacherasuser.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = hasattr(self.request.user, 'teacher') and self.request.user.teacher
        print(f'The Teacher is: {teacher}')
        allocated_subjects = SubjectAllocationModel.objects.filter(teacher=teacher)
        subject_count = allocated_subjects.count()
        context['allocated_subjects'] = allocated_subjects
        context['subject_count'] = subject_count
        return context
    

#This is for allocating the subjects to the teacher for the respective deparments
class TeacherAllocatedSubjectListView(TeacherRequiredMixin, ListView):
    model = SubjectAllocationModel
    template_name = 'TeacherAllocatedSubjectList.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.request.user.teacher
        allocated_subjects = SubjectAllocationModel.objects.filter(teacher=teacher)
        subject_count = allocated_subjects.count()
        context['allocated_subjects'] = allocated_subjects
        context['subject_count'] = subject_count
        return context


#This is the for the list of teachers of the respective department which can be accessed by the HOD 
class TeacherListView(SubAdminRequiredMixin, ListView):
    model = Teacher
    context_object_name = 'teachers'
    template_name = 'teacherlist.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher_department = hasattr(self.request.user, 'teacher') and self.request.user.teacher.teacher_department
        teacher_count = Teacher.objects.filter(teacher_department=teacher_department).count()
        context['teacher_count'] = teacher_count
        return context

    
#For Deleting the Teacher Added By the Department HOD
class TeacherDeleteView(AdminRequiredMixin, DeleteView):
    model = Teacher
    template_name = 'teacherdelete.html'
    success_url = reverse_lazy('uniapp:teacherlist')
    


class TeacherDetailView(Admin_And_HOD_Required_Mixin, DetailView):
    model = Teacher
    template_name = 'teacherdetail.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.object
        allocated_subjects = SubjectAllocationModel.objects.filter(teacher=teacher)
        context['allocated_subjects'] = allocated_subjects
        return context

class GraduateStudentsList(SubAdminRequiredMixin, ListView):
    model = Student
    template_name = 'graduatestudentslist.html'
    # paginate_by = 10
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher_department = self.request.user.teacher.teacher_department
        graduate_students = Student.objects.filter(student_department=teacher_department, student_semester__semester='Graduate')
        count = graduate_students.count()
        search_filter = GraduatesFilter(self.request.GET, queryset=graduate_students)
        graduate_students = search_filter.qs
        context['graduate_students'] = graduate_students
        context['count'] = count
        context['search_filter'] = search_filter
        return context


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class StudentListWithSemesterView(All_Except_Student_Mixin, ListView):
    model = Student
    template_name = 'studentlistwithsemester.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        semester_id = self.kwargs['semester_id']
        semester = Semester.objects.get(id=semester_id)
        hod_check = self.request.session.get('show_allocated_subjects', False)
        students = Student.objects.filter(student_semester_id=semester)
        student_semester_count = students.count()
        allocated_subejects = SubjectAllocationModel.objects.filter(semester=semester)
        marks_visible = {}
        for i in students:
            marks_visible[i.id] = i.marks_visible
        
        context['marks_visible'] = marks_visible
        context['hod_check'] = hod_check
        context['students'] = students
        context['allocated_subejects'] = allocated_subejects
        context['student_semester_count'] = student_semester_count
        context['semester'] = semester
        return context
    def post(self, request, *args, **kwargs):
        student_id = request.POST.get('student_id')
        marks_visible = request.POST.get('marks_visible') == 'true'
        student = Student.objects.get(id=student_id)
        student.marks_visible = marks_visible
        student.save()
        print(f"Student ID: {student_id}, Marks Visible: {marks_visible}")
        return JsonResponse({'success': True})
        

class StudentDeleteView(SubAdminRequiredMixin, DeleteView):
    model = Student
    template_name = 'studentdelete.html'
    def get_success_url(self):
        messages.success(self.request, f'The Student is Deleted Successully')
        if self.request.user.is_superuser:
            return reverse_lazy('uniapp:departments')
        elif self.request.user.teacher.is_sub_admin:
            return reverse_lazy('uniapp:semester')
    
class AllStudentListView(SubAdminRequiredMixin, ListView):
    model = Student
    template_name = 'allstudentlist.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher_department = self.request.user.teacher.teacher_department
        students = Student.objects.filter(student_department=teacher_department).exclude(student_semester__semester='Graduate')
        my_search = AllStudentsFilter(self.request.GET, queryset=students)
        students = my_search.qs
        student_count = students.count()
        context['students'] = students
        context['my_search'] = my_search
        context['student_count'] = student_count
        return context

class UpdateSemesterView(Admin_And_HOD_Required_Mixin, FormView):
    template_name = 'update_semester.html'
    form_class = SemesterUpdateForm
    success_url = reverse_lazy('uniapp:allstudentlist')

    def form_valid(self, form):
        new_semester = form.cleaned_data['student_semester']
        selected_student_ids = self.request.GET.getlist('selected_students')
        # Update the semesters of selected students
        Student.objects.filter(id__in=selected_student_ids).update(student_semester=new_semester)
        return super().form_valid(form)
    # def get_form(self, form_class=None):
    #     form = super().get_form(form_class)
    #     teacher = self.request.user.teacher
    #     form.fields['student_semester'].queryset = Semester.objects.filter(department=teacher.teacher_department)
    #     return form

def load_province(request):
    country_id = request.GET.get('nationality')
    province = Province.objects.filter(country_id=country_id)
    print('The view is also working')
    return JsonResponse(list(province.values('id', 'name')), safe=False)

def load_district(request):
    province_id = request.GET.get('province')
    district = District.objects.filter(province_id=province_id)
    print('District view is also working')
    return JsonResponse(list(district.values('id', 'name')), safe=False)

class StudentCreateView(SubAdminRequiredMixin, CreateView):
    form_class = AllStudentCreateForm
    template_name = 'allstudentcreate.html'
    success_url = reverse_lazy("uniapp:allstudentlist")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.instance.student_department = self.request.user.teacher.teacher_department
        teacher = self.request.user.teacher
        form.fields['student_semester'].queryset = Semester.objects.filter(department=teacher.teacher_department)
        return form
    def form_valid(self, form):
        response = super().form_valid(form)
        # Automatically allocate subjects to this student based on the semester
        allocated_subjects = SubjectAllocationModel.objects.filter(semester=self.object.student_semester).exclude(teacher=None)
        for subject_allocation in allocated_subjects:
            SubjectAllocationModel.objects.get_or_create(
                semester=self.object.student_semester,
                subject=subject_allocation.subject,
                student=self.object,
                teacher=None,
                department=self.object.student_department
            )
        return response

    def get_success_url(self):
        messages.success(self.request, f'The Student is Successully Added')
        return reverse_lazy('uniapp:allstudentlist')
        


class StudentCreateSemesterView(LoginRequiredMixin, CreateView):
    form_class = SemesterStudentCreateForm
    template_name = 'studentcreate.html'
    context_object_name = 'semes'
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        global semester
        semester_id = self.kwargs['semester_id']
        semester = Semester.objects.get(id=semester_id)
        if hasattr(self.request.user, 'teacher'):
            form.instance.student_department = self.request.user.teacher.teacher_department
            form.instance.student_semester = semester
        else:
            form.instance.student_department = semester.department
            form.instance.student_semester = semester
        return form
    def form_valid(self, form):
        response = super().form_valid(form)
        # Automatically allocate subjects to this student based on the semester
        allocated_subjects = SubjectAllocationModel.objects.filter(semester=self.object.student_semester).exclude(teacher=None)
        for subject_allocation in allocated_subjects:
            SubjectAllocationModel.objects.get_or_create(
                semester=self.object.student_semester,
                subject=subject_allocation.subject,
                student=self.object,
                teacher=None,
                department=self.object.student_department
            )
        return response
    def get_success_url(self):
        messages.success(self.request, f'The Student is Successully Added')
        if self.request.user.is_superuser:
            return reverse_lazy('uniapp:departments')
        elif self.request.user.teacher.is_sub_admin:
            return reverse_lazy('uniapp:semester')
        

    
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class StudentDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = 'studentdetail.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = hasattr(self.request.user, 'teacher') and self.request.user.teacher
        student_id = self.kwargs['pk']
        hod_check = self.request.session.get('show_allocated_subjects', False)
        student = Student.objects.get(id=student_id)
        semester = student.student_semester
        if teacher and teacher.is_sub_admin != True:
            # teacher = self.request.user.teacher
            subjects_teacher = SubjectAllocationModel.objects.filter(semester=semester,
            teacher=teacher)
            context['subjects'] = subjects_teacher
        elif teacher and teacher.is_sub_admin == True and hod_check == True:
            # teacher = self.request.user.teacher
            subjects_teacher = SubjectAllocationModel.objects.filter(semester=semester,
            teacher=teacher)
            context['subjects'] = subjects_teacher
        else:
            subjects_hod = SubjectAllocationModel.objects.filter(semester=semester)
            context['subjects_hod'] = subjects_hod
        
        return context
        

class StudentAttendenceDateView(ListView):
    model = AttendenceReport
    template_name = 'studentattendence.html'
    context_object_name = 'attendances'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subject_id = self.kwargs['subjectallocationmodel_id']
        student_id = self.kwargs['student_id']
        sub = SubjectAllocationModel.objects.get(id=subject_id)
        student = Student.objects.get(id=student_id)
        student_name = student.student_name
        subject = sub.subject
        attendences = AttendenceReport.objects.filter(attendence_id__attendence_subject=subject, attendence_student_id=student_id)
        attendence_count = attendences.count()
        present = AttendenceReport.objects.filter(attendence_id__attendence_subject=subject, attendence_student_id=student_id, attendence_status='Present').count()
        absent = AttendenceReport.objects.filter(attendence_id__attendence_subject=subject, attendence_student_id=student_id, attendence_status='Absent').count()
        if present == 0 and absent == 0:
            attendence_percentage = 0
        else:
            attendence_percentage = round((present/attendence_count)*100)
        context['attendences'] = attendences
        context['present'] = present
        context['absent'] = absent
        context['attendence_percentage'] = attendence_percentage
        context['student_name'] = student_name
        context['subject'] = subject
        return context


class StudentUpdateView(Admin_And_HOD_Required_Mixin, UpdateView):
    model = Student
    form_class = StudentUpdateForm
    template_name = 'studentupdate.html'
    success_url = reverse_lazy('uniapp:allstudentlist')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['marks_visible'].queryset = False
        print('The student is successfully updated')
        return form
    def form_valid(self, form):
        response = super().form_valid(form)
        # Automatically allocate subjects to this student based on the semester
        allocated_subjects = SubjectAllocationModel.objects.filter(semester=self.object.student_semester).exclude(teacher=None)
        for subject_allocation in allocated_subjects:
            SubjectAllocationModel.objects.get_or_create(
                semester=self.object.student_semester,
                subject=subject_allocation.subject,
                student=self.object,
                teacher=None,
                department=self.object.student_department
            )
        return response
    def get_success_url(self):
        messages.success(self.request, f'The Student is Successully Updated')
        if self.request.user.is_superuser:
            return reverse_lazy('uniapp:departments')
        elif self.request.user.teacher.is_sub_admin:
            return reverse_lazy('uniapp:allstudentlist')
    

def load_semesters(request):
    department_id = request.GET.get('student_department')
    semesters = Semester.objects.filter(department_id=department_id)
    return JsonResponse(list(semesters.values('id', 'semester')), safe=False)
    # pass

class SubjectListView(LoginRequiredMixin, ListView):
    model = Subject
    template_name = 'subjectlist.html'
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        if hasattr(self.request.user, 'teacher'):
            teacher_department = self.request.user.teacher.teacher_department
            subjects = Subject.objects.filter(subject_department=teacher_department)
            subject_count = subjects.count()
            context['subjects'] = subjects
            context['subject_count'] = subject_count
        elif hasattr(self.request.user, 'is_superuser'):
            subjects = Subject.objects.all()
            subject_count = subjects.count()
            context['subjects'] = subjects
            context['subject_count'] = subject_count
        return context

class SubjectCreateView(LoginRequiredMixin, CreateView):
    form_class = SubjectCreateForm
    template_name = 'subjectcreate.html'
    success_url = reverse_lazy('uniapp:subjectcreate')
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        
        if hasattr(self.request.user, 'teacher'):
            department = self.request.user.teacher.teacher_department
            form.instance.subject_department = department
            print(f'The Subject is Added {department}')
        return form
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'The Subject is Added Successully')
        return response
    
class SubjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Subject
    form_class = SubjectUpdateForm
    template_name = 'subjectupdate.html'
    success_url = reverse_lazy('uniapp:subjectlist')
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if hasattr(self.request.user, 'teacher'):
            form.instance.subject_department = self.request.user.teacher.teacher_department
        return form
    
    
class SubjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Subject
    template_name = 'subjectdelete.html'
    success_url = reverse_lazy('uniapp:subjectlist')
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'The Subject is Deleted Successully')
        return 
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        subject_id = self.kwargs['pk']
        print(f'The Subject Id is: {subject_id}')
        context["subject_id"] = subject_id
        return context
    

class SubjectAllocationCreateView(LoginRequiredMixin, CreateView):
    form_class = SubjectAllocationForm
    template_name = 'subjectallocation.html'
    success_url = reverse_lazy('uniapp:subjectallocation')
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        teacher_department = hasattr(self.request.user, 'teacher') and self.request.user.teacher.teacher_department
        form.instance.student_department = teacher_department
        form.fields['semester'].queryset = Semester.objects.filter(department=teacher_department).exclude(semester='Graduate')       
        return form
    def form_valid(self, form):
        subject = form.cleaned_data['subject']
        teacher = form.cleaned_data['teacher']
        semester = form.cleaned_data['semester']
        department = self.request.user.teacher.teacher_department
        existing_allocated_subjects = SubjectAllocationModel.objects.filter(teacher=teacher, subject=subject, semester=semester, department=department).exists()
        if not existing_allocated_subjects:
            allocation_teacher = SubjectAllocationModel(teacher=teacher, subject=subject, semester=semester, department=department)
            allocation_teacher.save()
        students_in_semester = Student.objects.filter(student_semester=semester, student_department=department)
        for student in students_in_semester:
            if SubjectAllocationModel.objects.filter(subject=subject, student=student).exists():
                pass
            else:
                allocation_student = SubjectAllocationModel(semester=semester, subject=subject, student=student, department=department)
                allocation_student.save()
        messages.success(self.request, f'The {subject} is Successully Allocated To {teacher.teacher_name}')
        return redirect(self.success_url)

class SubjectAllocationListView(LoginRequiredMixin, ListView):
    model = SubjectAllocationModel
    template_name = 'subjectallocationlist.html'
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        teacher = hasattr(self.request.user, 'teacher') and self.request.user.teacher
        subjectallocations = SubjectAllocationModel.objects.all().exclude(teacher=None)
        context['subjectallocations'] = subjectallocations
        return context

class SubjectAllocationUpdateView(LoginRequiredMixin, UpdateView):
    model = SubjectAllocationModel
    form_class = SubjectAllocationForm
    template_name = 'subjectallocationupdate.html'
    success_url = reverse_lazy('uniapp:semester')
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        teacher_department = hasattr(self.request.user, 'teacher') and self.request.user.teacher.teacher_department
        form.fields['semester'].queryset = Semester.objects.filter(department=teacher_department).exclude(semester='Graduate')       
        return form
    
class SubjectAllocationDeleteView(LoginRequiredMixin, DeleteView):
    model = SubjectAllocationModel
    template_name = 'subjectallocationdelete.html'
    success_url = reverse_lazy('uniapp:semester')

class SemesterListView(SubAdminRequiredMixin, ListView):
    model = Semester
    template_name = 'semester.html'
    
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        department = hasattr(self.request.user, 'teacher') and self.request.user.teacher.teacher_department
        semesters = Semester.objects.filter(department=department).exclude(semester='Graduate')
        context['semesters'] = semesters
        return context

    


def MarkAttendanceView(request, semester_id, subjectallocationmodel_id):
    semester = Semester.objects.get(id=semester_id)
    department = Department.objects.get(depart_name=semester.department)
    subject = SubjectAllocationModel.objects.get(id=subjectallocationmodel_id)
    subject_name = subject.subject
    teacher = subject.teacher
    students = Student.objects.filter(student_semester=semester)
    student_count = students.count()
    if request.method == 'POST':
        date = request.POST.get('date')
        att_department = department
        att_semester = semester
        att_subject = subject_name
        present_students = request.POST.getlist('present')
        attendence = Attendence(attendence_date=date,
                                 attendence_department=att_department, 
                                 attendence_semester=att_semester,
                                 attendence_subject=att_subject
                                 )
        attendence.save()
        student_list = Student.objects.filter(student_semester=semester)
        hod_check = request.session.get('show_allocated_subjects', False)
        for student in student_list:
            attendence_status = 'Present' if str(student.id) in present_students else 'Absent'
            attendance_report = AttendenceReport(
                attendence_student=student,
                attendence_id = attendence,
                attendence_status = attendence_status,  
            )
            attendance_report.save()
            messages.success(request, 'The Attendance is Saved Successfully')
        if request.user.teacher.is_sub_admin and hod_check != True:
            return redirect('uniapp:teacher_admin_dashboard')

        elif request.user.teacher.is_sub_admin and hod_check:
            return redirect('uniapp:teacher')
        else:
            return redirect('uniapp:teacher')
    context = {
        'students':students,
        'teacher':teacher,
        'student_count':student_count,
        'department':department,
        'semester':semester,
        'subject_name':subject_name,
        'subject_id':subjectallocationmodel_id,
 
    }
    return render(request, 'attendence.html', context)

class AttendenceSubjectView(LoginRequiredMixin, ListView):
    model = SubjectAllocationModel
    template_name = 'attendencesubject.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hod_check = self.request.session.get('show_allocated_subjects', False)
        # if hasattr(self.request.user, 'teacher') and self.request.user.teacher.is_sub_admin or self.request.user.is_superuser:
            
        if hasattr(self.request.user, 'teacher') and self.request.user.teacher.is_sub_admin  and hod_check != True or self.request.user.is_superuser:
            semester_id = self.kwargs['semester_id']
            semester = Semester.objects.get(id=semester_id)
            department = Department.objects.get(depart_name=semester.department)
            
            subjects = SubjectAllocationModel.objects.filter(
                department=department,
                semester=semester,
            ).exclude(teacher=None)
            subject_count = subjects.count()
            context['subjects'] = subjects
            context['subject_count'] = subject_count
            context['department'] = department
            context['semester'] = semester
            
        elif hasattr(self.request.user, 'teacher') and self.request.user.teacher.is_sub_admin  and hod_check == True:
            teacher = hasattr(self.request.user, 'teacher') and self.request.user.teacher
            subjects = SubjectAllocationModel.objects.filter(
                teacher=teacher
            )
            subject_count = subjects.count()
            context['subjects'] = subjects
            context['subject_count'] = subject_count
        elif hasattr(self.request.user, 'teacher') and self.request.user.teacher:
            teacher = hasattr(self.request.user, 'teacher') and self.request.user.teacher    
            subjects = SubjectAllocationModel.objects.filter(
                teacher=teacher
            )
            subject_count = subjects.count()
            context['subjects'] = subjects
            context['subject_count'] = subject_count

        
        return context

class AttendenceDateView(ListView):
    context_object_name = 'attendences'
    template_name = 'attendencedate.html'
    queryset = Attendence.objects.order_by('-attendence_date')
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        subject_id = self.kwargs['subjectallocationmodel_id']
        subject = SubjectAllocationModel.objects.get(
            id = subject_id
        )
        department = subject.department
        semester = subject.semester
        subject_name = subject.subject
        attendences = Attendence.objects.filter(
            attendence_subject = subject_name, attendence_semester=semester
        ) 
        classes_count = attendences.count()  
        context['attendences'] = attendences
        context['department'] = department
        context['semester'] = semester
        context['subject_name'] = subject_name
        context['classes_count'] = classes_count
        return context

class AttendenceDateDeleteView(LoginRequiredMixin, DeleteView):
    model = Attendence
    template_name = 'attendenceDateDelete.html'
    context_object_name = 'attendence'
    def get_success_url(self):
        return reverse_lazy('uniapp:teacher' )

class AttendenceDateUpdateView(LoginRequiredMixin, UpdateView):
    model = Attendence
    template_name = 'attendenceDateUpdate.html'
    context_object_name = 'attendence'
    form_class = AttendenceDateUpdateForm
    def get_success_url(self):
        return reverse_lazy('uniapp:teacher' )

class AttendenceDetailView(DetailView):
    model = Attendence
    template_name = 'attendencedetail.html'
    context_object_name = 'attendence'
    pk_url_kwarg = 'attendence_id'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        attendence = self.get_object()
        date = attendence.attendence_date
        semester = attendence.attendence_semester
        department = attendence.attendence_department
        subject = attendence.attendence_subject
        present_count = AttendenceReport.objects.filter(attendence_id__attendence_semester=semester, attendence_id__attendence_department=department,attendence_id__attendence_date=date, attendence_status='Present').count()
        absent_count = AttendenceReport.objects.filter(attendence_id__attendence_semester=semester, attendence_id__attendence_department=department,attendence_id__attendence_date=date, attendence_status='Absent').count()
        context['present_count'] = present_count
        context['absent_count'] = absent_count
        context['department'] = department
        context['semester'] = semester
        context['subject'] = subject
        context['date'] = date
        return context

class AttendenceUpdateView(LoginRequiredMixin, UpdateView):
    model = AttendenceReport
    template_name = 'attendenceupdate.html'
    fields = ['attendence_status']
    def post(self, request, *args, **kwargs):
        attendence_status = request.POST.get('attendence_status')
        self.object = self.get_object()
        if attendence_status:
            self.object.attendence_status = 'Present'
        else:
            self.object.attendence_status = 'Absent'
        self.object.save()
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        attendence_id = self.kwargs['pk']
        attendence = AttendenceReport.objects.get(id=attendence_id)
        student = attendence.attendence_student
        subject = attendence.attendence_id
        messages.success(self.request, f'The Attendance is Updated Successfully')
        context["student"] = student
        context["subject"] = subject
        return context
    
    def get_success_url(self):
        return redirect('uniapp:attendencedetail', args=[self.kwargs['pk']])


class AttendenceDetailDeleteView(LoginRequiredMixin, DeleteView):
    model = AttendenceReport
    template_name = 'attendenceDateDelete.html'
    context_object_name = 'attendence'
    def get_success_url(self):
        return reverse_lazy('uniapp:teacher' )  

def update_session(request):
    if request.method == 'POST':
        hod_check = request.POST.get('show_allocated_subjects') == 'on'
        request.session['show_allocated_subjects'] = hod_check
        request.session.modified = True

        print(f'the update_session works {hod_check}')
        return HttpResponse('Session updated successfully')  # Simple response to acknowledge success
    else:
        return redirect('uniapp:teacher_admin_dashboard')



class AssessmentSubjectView(LoginRequiredMixin, ListView):
    model = SubjectAllocationModel
    template_name = 'AssessmentSubject.html'
    
    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)
        teacher = hasattr(self.request.user, 'teacher') and self.request.user.teacher
        hod = hasattr(self.request.user, 'teacher') and self.request.user.teacher.is_sub_admin
        hod_check = self.request.session.get('show_allocated_subjects', False)
        student_id = self.kwargs['student_id']
        student = Student.objects.get(id=student_id)
        student_department = student.student_department
        if teacher and teacher.is_sub_admin != True:
            subjects = SubjectAllocationModel.objects.filter(
                    department=student.student_department,
                    semester=student.student_semester,
                    teacher=teacher
                )
            subjects_count = subjects.count()
            context['subjects'] = subjects
            context['subjects_count'] = subjects_count
        elif teacher and teacher.is_sub_admin == True and hod_check == True:
            subjects = SubjectAllocationModel.objects.filter(
                    department=student.student_department,
                    semester=student.student_semester,
                    teacher=teacher
                )
            subjects_count = subjects.count()
            context['subjects'] = subjects
            context['subjects_count'] = subjects_count
        
        else:
            subjects = SubjectAllocationModel.objects.filter(
                    department=student.student_department,
                    semester=student.student_semester,
                    student=student
                )
            subjects_count = subjects.count()
            context['subjects'] = subjects
            context['subjects_count'] = subjects_count

        context['hod'] = hod
        context['hod_check'] = hod_check
        context['teacher'] = teacher
        context['student_id'] = student_id
        context['student'] = student
        context['student_department'] = student_department
        self.request.session['student_id'] = student_id
        return context
    


class Assessment(TemplateView):
    template_name = 'assessment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student_id = self.request.session.get('student_id')
        subject_id = self.kwargs['subjectallocationmodel_id']
        sub = SubjectAllocationModel.objects.get(id=subject_id)
        subject = sub.subject
        teacher = sub.teacher
        student = Student.objects.get(id=student_id)
        marks_visible = student.marks_visible
        context['student'] = student
        context['subject'] = subject
        context['teacher'] = teacher
        context['marks_visible'] = marks_visible
        return context
        
def Update_The_Result(self):
    student_id = self.request.session.get('student_id')
    subject_id = self.kwargs['subjectallocationmodel_id']
    subject = SubjectAllocationModel.objects.get(id=subject_id)
    subject_name = subject.subject
    student = Student.objects.get(id=student_id)
    semester = student.student_semester
    assignment = Assignment.objects.filter(subject_allocation=subject_name, student=student, semester=semester)
    quiz = Quiz.objects.filter(subject_allocation=subject_name, student=student, semester=semester)
    presentation = Presentation.objects.filter(subject_allocation=subject_name, student=student, semester=semester)
    mid = Mid.objects.filter(subject_allocation=subject_name, student=student, semester=semester)
    final = Final.objects.filter(subject_allocation=subject_name, student=student, semester=semester)
    assignment_marks = assignment.aggregate(total=Sum('marks')).get('total') or 0
    quiz_marks = quiz.aggregate(total=Sum('marks')).get('total') or 0
    presentation_marks = presentation.aggregate(total=Sum('marks')).get('total') or 0
    mid_marks = mid.aggregate(total=Sum('marks')).get('total') or 0
    final_marks = final.aggregate(total=Sum('marks')).get('total') or 0
    total_marks = assignment_marks + quiz_marks + presentation_marks + mid_marks +final_marks  
    result, created = PaperResult.objects.get_or_create(student=student, semester=semester, subject_allocation=str(subject_name))

    if total_marks >= 85:
        result.gp = 4.00
        result.grade = 'A'
    elif 80 <= total_marks < 85:
        result.gp = 3.70
        result.grade = 'A-'
    elif 75 <= total_marks < 80:
        result.gp = 3.30
        result.grade = 'B+'
    elif 70 <= total_marks < 75:
        result.gp = 3.00
        result.grade = 'B'
    elif 65 <= total_marks < 70:
        result.gp = 2.70
        result.grade = 'B-'
    elif 61 <= total_marks < 65:
        result.gp = 2.30
        result.grade = 'C+'
    elif 58 <= total_marks < 61:
        result.gp = 2.00
        result.grade = 'C'
    elif 55 <= total_marks < 58:
        result.gp = 1.70
        result.grade = 'C-'
    elif 50 <= total_marks < 55:
        result.gp = 1.00
        result.grade = 'D'
    else:
        result.gp = 0.00
        result.grade = 'F'

    result.marks = total_marks
    result.total_marks = 100
    result.credit_hours = subject.subject.credit_hours
    result.qp = result.gp * result.credit_hours
    result.save()

def all_subjects_marks_view(self):
    student_id = self.request.session.get('student_id')
    student = get_object_or_404(Student, id=student_id)
    semester = student.student_semester
    obtained_marks = 0
    total_marks = 0
    gpa = 0
    t_qp = 0
    t_credit_hours = 0
    percentage = 0

    if student.student_semester != 'Graduate':
        paper_result = PaperResult.objects.filter(student=student, semester=semester)
        
        for i in paper_result:
            cr_h = i.credit_hours
            t_credit_hours += cr_h
        
        obtained_marks = paper_result.aggregate(total=Sum('marks')).get('total') or 0
        total_marks = paper_result.aggregate(total=Sum('total_marks')).get('total') or 0
        gpa = paper_result.aggregate(total=Sum('gp')).get('total') or 0
        t_qp = paper_result.aggregate(total=Sum('qp')).get('total') or 0

        result, created = Result.objects.get_or_create(student=student, semester=semester)
        result.marks = obtained_marks
        result.total_marks = total_marks
        if len(paper_result) == 0:
            result.gpa == 0
        else:
            result.gpa = gpa / len(paper_result)
        result.t_qp = t_qp
        result.t_credit_hours = t_credit_hours

        if result.total_marks == 0:
            result.percentage = 0.00
        else:
            result.percentage = (obtained_marks / total_marks) * 100
        result.save()        

def Add_assessment(self):
    global subject_name, student, teacher, semester, subject_semester
    student_id = self.request.session.get('student_id')
    subject_id = self.kwargs['subjectallocationmodel_id']
    print(f"this id is coming from view +++{student_id}/{subject_id}")
    subject_allocation = SubjectAllocationModel.objects.get(id=subject_id)
    teacher = subject_allocation.teacher
    subject_semester = subject_allocation.semester
    student = Student.objects.get(id=student_id)
    semester = student.student_semester
    subject_name = subject_allocation.subject.subject_name
    form.instance.subject_allocation = subject_name
    form.instance.student = student
    form.instance.semester = semester
    self.request.session['subject_id'] = subject_id

class AssignmentAddView(TeacherRequiredMarksMixin, CreateView):
    form_class = AssignmentForm
    template_name = 'assignmentAdd.html'
    def get_form(self, form_class=None):
        global form
        form = super().get_form(form_class)
        Add_assessment(self)
        return form
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        Update_The_Result(self)
        all_subjects_marks_view(self)
        context["teacher"] = teacher
        context["student"] = student
        context["subject_name"] = subject_name
        context["subject_semester"] = subject_semester
        context["semester"] = semester
        return context
    def get_success_url(self):
        return reverse_lazy('uniapp:assignmentAdd', args=[self.kwargs['subjectallocationmodel_id']])

def View_assessment(self):
    global student, marks_visible, subject_name
    student_id = self.request.session.get('student_id')
    subject_id = self.kwargs['subjectallocationmodel_id']
    subject = SubjectAllocationModel.objects.get(id=subject_id)
    subject_name = subject.subject
    student = Student.objects.get(id=student_id)
    marks_visible = student.marks_visible
    self.request.session['subject_id'] = subject_id

class AssignmentView(LoginRequiredMixin, ListView):
    model = Assignment
    template_name = 'assignmentView.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        View_assessment(self)
        assignments = Assignment.objects.filter(student=student, subject_allocation=subject_name)
        assignments_count = assignments.count()
        total_marks = assignments.aggregate(total=Sum('marks')).get('total') or 0
        total_obtained_marks = assignments.aggregate(total=Sum('total_marks')).get('total') or 0
        context['assignments'] = assignments
        context['assignments_count'] = assignments_count
        context['total_marks'] = total_marks
        context['total_obtained_marks'] = total_obtained_marks
        context['student'] = student
        context['marks_visible'] = marks_visible
        context['subject_name'] = subject_name
        return context

def Update_assessment(self):
    student = this_item.student
    subject = this_item.subject_allocation
    semester = this_item.semester
    subject_id = self.request.session.get('subject_id')
    assignment = Assignment.objects.filter(subject_allocation=subject, student=student, semester=semester)
    quiz = Quiz.objects.filter(subject_allocation=subject, student=student, semester=semester)
    presentation = Presentation.objects.filter(subject_allocation=subject, student=student, semester=semester)
    mid = Mid.objects.filter(subject_allocation=subject, student=student, semester=semester)
    final = Final.objects.filter(subject_allocation=subject, student=student, semester=semester)
    assignment_marks = assignment.aggregate(total=Sum('marks')).get('total') or 0
    quiz_marks = quiz.aggregate(total=Sum('marks')).get('total') or 0
    presentation_marks = presentation.aggregate(total=Sum('marks')).get('total') or 0
    mid_marks = mid.aggregate(total=Sum('marks')).get('total') or 0
    final_marks = final.aggregate(total=Sum('marks')).get('total') or 0
    paper_result, created = PaperResult.objects.get_or_create(student=student, semester=semester, subject_allocation=subject)
    # Update fields in PaperResult based on your form data
    paper_result.marks = (
        assignment_marks +
        quiz_marks +
        presentation_marks +
        mid_marks +
        final_marks
    )
    total_marks = paper_result.marks
    if total_marks >= 85:
        paper_result.gp = 4.00
        paper_result.grade = 'A'
    elif total_marks >= 80 and total_marks <= 84:
        paper_result.gp = 3.70
        paper_result.grade = 'A-'
    elif total_marks >= 75 and total_marks <= 79:
        paper_result.gp = 3.30
        paper_result.grade = 'B+'
    elif total_marks >= 70 and total_marks <= 74:
        paper_result.gp = 3.00
        paper_result.grade = 'B'
    elif total_marks >= 65 and total_marks <= 69:
        paper_result.gp = 2.70
        paper_result.grade = 'B-'
    elif total_marks >= 61 and total_marks <= 64:
        paper_result.gp = 2.30
        paper_result.grade = 'C+'
    elif total_marks >= 58 and total_marks <= 60:
        paper_result.gp = 2.00
        paper_result.grade = 'C'
    elif total_marks >= 55 and total_marks <= 57:
        paper_result.gp = 1.70
        paper_result.grade = 'C-'
    elif total_marks >= 50 and total_marks <= 54:
        paper_result.gp = 1.00
        paper_result.grade = 'D'
    elif total_marks < 50:
        paper_result.gp = 0.00
        paper_result.grade = 'F'
    
    # Update fields in Result based on your form data
    paper_result.qp = paper_result.gp * paper_result.credit_hours
    # Update other fields in Result based on your form data
    paper_result.save()
    result, created = Result.objects.get_or_create(student=student, semester=semester)
    if student.student_semester != 'Graduate':
        paper_result = PaperResult.objects.filter(student=student, semester=semester)
        obtained_marks = paper_result.aggregate(total=Sum('marks')).get('total') or 0
        total_marks = paper_result.aggregate(total=Sum('total_marks')).get('total') or 0
        gpa = paper_result.aggregate(total=Sum('gp')).get('total') or 0
        t_qp = paper_result.aggregate(total=Sum('qp')).get('total') or 0

        result, created = Result.objects.get_or_create(student=student, semester=semester)
        result.marks = obtained_marks
        result.total_marks = total_marks
        
        result.t_qp = round(t_qp, 2)
        result.gpa = round((gpa / len(paper_result)), 2)
        if result.total_marks == 0:
            result.percentage = 0
        else:
            result.percentage = round(((obtained_marks / total_marks) * 100), 2)

        result.save()

class AssignmentUpdateView(AssessementUpdateMixin, UpdateView):
    model = Assignment
    form_class = AssignmentUpdateForm
    template_name = 'assignmentUpdate.html'
    def form_valid(self, form):
        
        global this_item
        this_item = form.save()
        Update_assessment(self)
        return redirect(reverse('uniapp:assignmentUpdate', args=[self.kwargs['pk']]))


def Delete_assessment():
    student = this_object.student
    subject = this_object.subject_allocation
    semester = this_object.semester
    assignment = Assignment.objects.filter(subject_allocation=subject, student=student,semester=semester)
    quiz = Quiz.objects.filter(subject_allocation=subject, student=student,semester=semester)
    presentation = Presentation.objects.filter(subject_allocation=subject,student=student, semester=semester)
    mid = Mid.objects.filter(subject_allocation=subject, student=student,semester=semester)
    final = Final.objects.filter(subject_allocation=subject, student=student,semester=semester)
    assignment_marks = assignment.aggregate(total=Sum('marks')).get('total') or 0
    quiz_marks = quiz.aggregate(total=Sum('marks')).get('total') or 0
    presentation_marks = presentation.aggregate(total=Sum('marks')).get('total') or 0
    mid_marks = mid.aggregate(total=Sum('marks')).get('total') or 0
    final_marks = final.aggregate(total=Sum('marks')).get('total') or 0
    paper_result, created = PaperResult.objects.get_or_create(student=student,semester=semester, subject_allocation=subject)
    paper_result.marks = (
        assignment_marks +
        quiz_marks +
        presentation_marks +
        mid_marks +
        final_marks
    )
    total_marks = paper_result.marks
    if total_marks >= 85:
        paper_result.gp = 4.00
        paper_result.grade = 'A'
    elif total_marks >= 80 and total_marks <= 84:
        paper_result.gp = 3.70
        paper_result.grade = 'A-'
    elif total_marks >= 75 and total_marks <= 79:
        paper_result.gp = 3.30
        paper_result.grade = 'B+'
    elif total_marks >= 70 and total_marks <= 74:
        paper_result.gp = 3.00
        paper_result.grade = 'B'
    elif total_marks >= 65 and total_marks <= 69:
        paper_result.gp = 2.70
        paper_result.grade = 'B-'
    elif total_marks >= 61 and total_marks <= 64:
        paper_result.gp = 2.30
        paper_result.grade = 'C+'
    elif total_marks >= 58 and total_marks <= 60:
        paper_result.gp = 2.00
        paper_result.grade = 'C'
    elif total_marks >= 55 and total_marks <= 57:
        paper_result.gp = 1.70
        paper_result.grade = 'C-'
    elif total_marks >= 50 and total_marks <= 54:
        paper_result.gp = 1.00
        paper_result.grade = 'D'
    elif total_marks < 50:
        paper_result.gp = 0.00
        paper_result.grade = 'F'
    
    # Update fields in Result based on your form data
    paper_result.qp = paper_result.gp * paper_result.credit_hours
    # Update other fields in Result based on your form data
    paper_result.save()
    result, created = Result.objects.get_or_create(student=student, semester=semester)
    if student.student_semester != 'Graduate':
        paper_result = PaperResult.objects.filter(student=student, semester=semester)
        obtained_marks = paper_result.aggregate(total=Sum('marks')).get('total') or 0
        total_marks = paper_result.aggregate(total=Sum('total_marks')).get('total') or 0
        gpa = paper_result.aggregate(total=Sum('gp')).get('total') or 0
        t_qp = paper_result.aggregate(total=Sum('qp')).get('total') or 0
        result, created = Result.objects.get_or_create(student=student, semester=semester)
        result.marks = obtained_marks
        result.total_marks = total_marks
            
        result.t_qp = round(t_qp, 2)
        result.gpa = round((gpa / len(paper_result)), 2)
        if result.total_marks == 0:
            result.percentage = 0
        else:
            result.percentage = round(((obtained_marks / total_marks) * 100), 2)
        print("total_marks:", total_marks)
        print("gpa:", gpa)
        print("len(paper_result):", len(paper_result))
        print("The Percentage is :", result.percentage)
        result.save()

class AssignmentDeleteView(AssessementUpdateMixin, DeleteView):
    model = Assignment
    template_name = 'assignmentDelete.html'
    context_object_name = 'assignment'
    def post(self, request, *args, **kwargs):
        # Fetch the assignment instance before deleting
        global this_object
        this_object = self.get_object()
        response = super().post(request, *args, **kwargs)
        Delete_assessment()
        return response 
    def get_success_url(self):
         return reverse_lazy('uniapp:admin_dashboard')
         
class QuizAddView(TeacherRequiredMarksMixin, CreateView):
    form_class = QuizForm
    template_name = 'quizAdd.html'
    def get_form(self, form_class=None):
        global form
        form = super().get_form(form_class)
        Add_assessment(self)
        return form
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        Update_The_Result(self)
        all_subjects_marks_view(self)
        context["teacher"] = teacher
        context["student"] = student
        context["subject_name"] = subject_name
        context["subject_semester"] = subject_semester
        context["semester"] = semester
        return context
    def get_success_url(self):
        return reverse_lazy('uniapp:quizAdd', args=[self.kwargs['subjectallocationmodel_id']])


class QuizView(ListView):
    model = Quiz
    template_name = 'quizView.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        View_assessment(self)
        quizs = Quiz.objects.filter(subject_allocation=subject_name, student=student)
        quizs_count = quizs.count()
        total_marks = quizs.aggregate(total=Sum('marks')).get('total') or 0
        total_obtained_marks = quizs.aggregate(total=Sum('total_marks')).get('total') or 0
        context['quizs'] = quizs
        context['student'] = student
        context['quizs_count'] = quizs_count
        context['total_marks'] = total_marks
        context['total_obtained_marks'] = total_obtained_marks
        context['subject_name'] = subject_name
        return context

class QuizUpdateView(TeacherRequiredMarksMixin, UpdateView):
    model = Quiz
    form_class = QuizUpdateForm
    template_name = 'quizUpdate.html'
    def form_valid(self, form):
        # Update Assignment
        global this_item
        this_item = form.save()
        Update_assessment()
        return redirect(reverse('uniapp:quizUpdate', args=[self.kwargs['pk']]))
    

class QuizDeleteView(TeacherRequiredMarksMixin, DeleteView):
    model = Quiz
    template_name = 'quizDelete.html'
    def post(self, request, *args, **kwargs):
        # Fetch the assignment instance before deleting
        global this_object
        this_object = self.get_object()
        response = super().post(request, *args, **kwargs)
        Delete_assessment()
        return response
    def get_success_url(self):
         return reverse_lazy('uniapp:admin_dashboard')

class PresentationAddView(TeacherRequiredMarksMixin, CreateView):
    form_class = PresentationForm
    template_name = 'presentationAdd.html'
    def get_form(self, form_class=None):
        global form
        form = super().get_form(form_class)
        Add_assessment(self)
        return form
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        Update_The_Result(self)
        all_subjects_marks_view(self)
        context["teacher"] = teacher
        context["student"] = student
        context["subject_name"] = subject_name
        context["subject_semester"] = subject_semester
        context["semester"] = semester
        return context
    def get_success_url(self):
        return reverse_lazy('uniapp:presentationAdd', args=[self.kwargs['subjectallocationmodel_id']])

class PresentationUpdateView(TeacherRequiredMarksMixin, UpdateView):
    model = Presentation
    form_class = PresentationUpdateForm
    template_name = 'presentationUpdate.html'
    def form_valid(self, form):
        # Update Assignment
        global this_item
        this_item = form.save()
        Update_assessment()
        return redirect(reverse('uniapp:presentationUpdate', args=[self.kwargs['pk']]))
    
class PresentationView(ListView):
    model = Presentation
    template_name = 'presentationView.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        View_assessment(self)
        presentations = Presentation.objects.filter(subject_allocation=subject_name, student=student)
        presentations_count = presentations.count()
        total_marks = presentations.aggregate(total=Sum('marks')).get('total') or 0
        total_obtained_marks = presentations.aggregate(total=Sum('total_marks')).get('total') or 0
        context['presentations_count'] = presentations_count
        context['total_marks'] = total_marks
        context['total_obtained_marks'] = total_obtained_marks
        context['presentations'] = presentations
        context['student'] = student
        context['subject_name'] = subject_name
        return context
    

class PresentationDeleteView(TeacherRequiredMarksMixin, DeleteView):
    model = Presentation
    template_name = 'presentationDelete.html'
    def post(self, request, *args, **kwargs):
        # Fetch the assignment instance before deleting
        global this_object
        this_object = self.get_object()
        response = super().post(request, *args, **kwargs)
        Delete_assessment()
        return response
    def get_success_url(self):
         return reverse_lazy('uniapp:admin_dashboard')

class MidAddView(TeacherRequiredMarksMixin, CreateView):
    form_class = MidForm
    template_name = 'midAdd.html'
    def get_form(self, form_class=None):
        global form
        form = super().get_form(form_class)
        Add_assessment(self)
        return form
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        Update_The_Result(self)
        all_subjects_marks_view(self)
        context["teacher"] = teacher
        context["student"] = student
        context["subject_name"] = subject_name
        context["subject_semester"] = subject_semester
        context["semester"] = semester
        return context
    def get_success_url(self):
        return reverse_lazy('uniapp:midAdd', args=[self.kwargs['subjectallocationmodel_id']])  

class MidView(ListView):
    model = Mid
    template_name = 'midView.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        View_assessment(self)
        mid = Mid.objects.filter(subject_allocation=subject_name, student=student)
        context['mid'] = mid
        context['student'] = student
        context['subject_name'] = subject_name
        return context

class MidUpdateView(TeacherRequiredMarksMixin, UpdateView):
    model = Mid
    form_class = MidUpdateForm
    template_name = 'midUpdate.html' 
    def form_valid(self, form):
        # Update Assignment
        global this_item
        this_item = form.save()
        Update_assessment()
        return redirect(reverse('uniapp:midUpdate', args=[self.kwargs['pk']]))

class MidDeleteView(TeacherRequiredMarksMixin, DeleteView):
    model = Mid
    template_name = 'midDelete.html'
    def post(self, request, *args, **kwargs):
        # Fetch the assignment instance before deleting
        global this_object
        this_object = self.get_object()
        response = super().post(request, *args, **kwargs)
        Delete_assessment()
        return response
    def get_success_url(self):
         return reverse_lazy('uniapp:admin_dashboard')

class FinalAddView(TeacherRequiredMarksMixin, CreateView):
    form_class = FinalForm
    template_name = 'finalAdd.html'
    def get_form(self, form_class=None):
        global form
        form = super().get_form(form_class)
        Add_assessment(self)
        return form
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        Update_The_Result(self)
        all_subjects_marks_view(self)
        context["teacher"] = teacher
        context["student"] = student
        context["subject_name"] = subject_name
        context["subject_semester"] = subject_semester
        context["semester"] = semester
        return context
    def get_success_url(self):
        return reverse_lazy('uniapp:finalAdd', args=[self.kwargs['subjectallocationmodel_id']])

class FinalView(ListView):
    model = Final
    template_name = 'finalView.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        View_assessment(self)
        final = Final.objects.filter(subject_allocation=subject_name, student=student)
        context['final'] = final
        context['student'] = student
        context['subject_name'] = subject_name
        return context

class FinalUpdateView(TeacherRequiredMarksMixin, UpdateView):
    model = Final
    form_class = FinalUpdateForm
    template_name = 'finalUpdate.html'
    def form_valid(self, form):
        # Update Assignment
        global this_item
        this_item = form.save()
        Update_assessment()
        return redirect(reverse('uniapp:finalUpdate', args=[self.kwargs['pk']]))

class FinalDeleteView(TeacherRequiredMarksMixin, DeleteView):
    model = Final
    template_name = 'finalDelete.html'
    def post(self, request, *args, **kwargs):
        # Fetch the assignment instance before deleting
        global this_object
        this_object = self.get_object()
        response = super().post(request, *args, **kwargs)
        Delete_assessment()
        return response
    def get_success_url(self):
         return reverse_lazy('uniapp:admin_dashboard')
class SubjectTotalMarksView(ListView):
    model = Result
    template_name = 'result.html'
    context_object_name = 'results'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student_id = self.request.session.get('student_id')
        subject_id = self.kwargs['subjectallocationmodel_id']
        subject = SubjectAllocationModel.objects.get(id=subject_id)
        subject_name = subject.subject
        student = Student.objects.get(id=student_id)
        
        # Get the student's current semester
        current_semester = student.student_semester

        # Try to fetch the assessments related to the specific subject and for all semesters
        # This ensures we get marks even if the student has graduated or changed semesters
        assignment = Assignment.objects.filter(subject_allocation=subject_name, student=student)
        quiz = Quiz.objects.filter(subject_allocation=subject_name, student=student)
        presentation = Presentation.objects.filter(subject_allocation=subject_name, student=student)
        mid = Mid.objects.filter(subject_allocation=subject_name, student=student)
        final = Final.objects.filter(subject_allocation=subject_name, student=student)
        
        # Calculate marks for all assessments
        assignment_marks = assignment.aggregate(total=Sum('marks')).get('total') or 0
        quiz_marks = quiz.aggregate(total=Sum('marks')).get('total') or 0
        presentation_marks = presentation.aggregate(total=Sum('marks')).get('total') or 0
        mid_marks = mid.aggregate(total=Sum('marks')).get('total') or 0
        final_marks = final.aggregate(total=Sum('marks')).get('total') or 0

        total_marks = assignment_marks + quiz_marks + presentation_marks + mid_marks + final_marks
        
        # Fetch the result object
        papers_result = PaperResult.objects.filter(student=student, subject_allocation=subject)
        
        # Pass the results to the context if they exist
        if papers_result.exists():
            result = papers_result.first()  # Assuming one result per subject/semester
            context['gp'] = result.gp
            context['qp'] = result.qp
            context['grade'] = result.grade
            context['total_marks'] = total_marks

        # Pass other information to the context
        context['papers_result'] = papers_result
        context['credit_hours'] = subject.subject.credit_hours
        context['subject_name'] = subject_name
        context['subject'] = subject
        context['student'] = student
        context['assignment_marks'] = assignment_marks
        context['quiz_marks'] = quiz_marks
        context['presentation_marks'] = presentation_marks
        context['mid_marks'] = mid_marks
        context['final_marks'] = final_marks

        return context



# class SubjectTotalMarksView(ListView):
#     model = Result
#     template_name = 'result.html'
#     context_object_name = 'results'
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         student_id = self.request.session.get('student_id')
#         subject_id = self.kwargs['subjectallocationmodel_id']
#         subject = SubjectAllocationModel.objects.get(id=subject_id)
#         subject_name = subject.subject
#         student = Student.objects.get(id=student_id)
#         semester = student.student_semester
#         assignment = Assignment.objects.filter(subject_allocation=subject_name, student=student, semester=semester)
#         quiz = Quiz.objects.filter(subject_allocation=subject_name, student=student, semester=semester)
#         presentation = Presentation.objects.filter(subject_allocation=subject_name, student=student, semester=semester)
#         mid = Mid.objects.filter(subject_allocation=subject_name, student=student, semester=semester)
#         final = Final.objects.filter(subject_allocation=subject_name, student=student, semester=semester)
#         assignment_marks = assignment.aggregate(total=Sum('marks')).get('total') or 0
#         quiz_marks = quiz.aggregate(total=Sum('marks')).get('total') or 0
#         presentation_marks = presentation.aggregate(total=Sum('marks')).get('total') or 0
#         mid_marks = mid.aggregate(total=Sum('marks')).get('total') or 0
#         final_marks = final.aggregate(total=Sum('marks')).get('total') or 0
#         total_marks = assignment_marks + quiz_marks + presentation_marks + mid_marks + final_marks
#         papers_result = PaperResult.objects.filter(student=student, subject_allocation=subject)
#         print(f'These are the marks /{subject_name}/{student}/{assignment_marks}/{quiz_marks}/{presentation_marks}/{final_marks}')
#         if papers_result.count() == 0:
#             pass
#         else:
#             for i in papers_result:
#                 gp = i.gp
#                 qp = i.qp
#                 grade = i.grade
#                 marks = i.marks
#             context['gp'] = gp
#             context['qp'] = qp
#             context['grade'] = grade
#             context['total_marks'] = total_marks
#         credit_hours = subject.subject.credit_hours
#         context['papers_result'] = papers_result
#         context['credit_hours'] = credit_hours
#         context['subject_name'] = subject_name
#         context['subject'] = subject
#         context['marks'] = subject_name
#         context['student'] = student
#         context['assignment_marks'] = assignment_marks
#         context['quiz_marks'] = quiz_marks
#         context['presentation_marks'] = presentation_marks
#         context['mid_marks'] = mid_marks
#         context['final_marks'] = final_marks
#         return context

        
class AllSubjectsMarksView(TemplateView):
    
    def get(self, request,*args, **kwargs):
        global student_name, s_id, department, pic, session, ad_year, result_date, issue_date
        result_id = [int(id) for id in request.GET.getlist('result_id')]
        result_date = request.GET.get('date_of_issue')
        issue_date = request.GET.get('result_declaration')
        record = Result.objects.filter(id__in=result_id)
        student_id = self.request.session.get('student_id')
        student = Student.objects.get(id=student_id)
        pic = student.profile_pic
        student_name = student.student_name
        department = student.student_department
        session = student.session
        ad_year = student.addmission_year
        results = Result.objects.filter(student=student)
        context = {
            'student' : student,
            'student_name' : student_name,
            'pic' : pic,
            'result_date' : result_date, 
            'issue_date' : issue_date, 
            'results' : results,
            'record' : record,
            'department' : department,
        }
        if request.GET.get('download_pdf'):
            pdf_file = self.render_to_pdf('allSubjectsMarks.html', context)
            response = HttpResponse(pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="selected_rows.pdf"'
            response.write(pdf_file)
            return response
        
        return render(request, 'allSubjectsMarks.html', context)   
    

    def render_to_pdf(self, template_path, context):
        template = get_template(template_path)
        html = template.render(context)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename=selected_rows.pdf'
        page_width, page_height = letter

        c = SimpleDocTemplate(response, pagesize=(page_width, page_height))
        
        all_tables = [Spacer(1, 200)]
        semesters_to_print = min(6, len(context['record']))
        semester_counter = 0
        for records in context['record']:
            papers = PaperResult.objects.filter(semester=records.semester, student=records.student)
            data = [[f"{session} {ad_year}"],
            ["Course Code", "Course Title",  "Credit Hours", "Marks(100)", "Grade Points", "Quality Points", "Grade"]
            ]
            for paper in papers:
                data.append(['Eng-123', 
                            paper.subject_allocation, 
                            paper.credit_hours,
                            paper.marks, 
                            paper.gp,
                            paper.qp,
                            paper.grade,
                            ])
            
            percentage = records.percentage   
            gpa =  records.gpa
            data.append([f"Percentage:", f"{percentage}","Grade Point Averages(GPA):","","","", f"{gpa}"] )
            row_heights = [8, 7.5]
            row_heights.extend([7.5] * len(papers))
            row_heights.extend([8.5])
            table = Table(data, colWidths=[65, 200, 50, 50, 50, 50, 40], rowHeights=row_heights)
            
            # Apply styles to the table
            
            style = TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), colors.rgb2cmyk(31, 78, 120)),
                                ('BACKGROUND', (0, 1), (-1, 1), colors.wheat),
                                ('FONTSIZE', (0, 0), (-1, 0), 9),
                                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                ('TOPPADDING', (0, 1), (-1, 1), 5),
                                ('FONTSIZE', (0, 1), (-1, 1), 7),
                                ('FONTNAME', (0, 1), (-1, 1), 'Times-Bold'),
                                ('FONTNAME', (0, 2), (-1, -2), 'Times-Roman'),
                                ('FONTNAME', (0, -1), (0, -1), 'Times-Bold'),
                                ('FONTNAME', (1, -1), (1, -1), 'Times-Roman'),
                                ('FONTNAME', (2, -1), (5, -1), 'Times-Bold'),
                                ('FONTNAME', (-1, -1), (-1, -1), 'Times-Roman'),
                                ('FONTSIZE', (0, 2), (-1, -1), 8),
                                ('SPAN', (0, 0), (-1, 0)),
                                ('SPAN', (2, -1), (5, -1)),
                                ('ALIGN', (2, -1), (5, -1), 'RIGHT'),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                ('ALIGN', (0, 0), (-1, 1), 'CENTER'),
                                ('ALIGN', (2, 1), (-1, -2), 'CENTER'),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                                ('TOPPADDING', (0, 2), (-1, -1), 4),
                                ('LEFTPADDING', (0, 2), (-1, -1), 1),
                                ('GRID', (0, 0), (-1, 1), 0, colors.black), 
                                ('LINEBEFORE', (0, 0), (0, -1), 0, colors.black), 
                                ('LINEBEFORE', (1, 0), (1, -2), 0, colors.black), 
                                ('LINEBEFORE', (2, 0), (2, -2), 0, colors.black), 
                                ('LINEBEFORE', (3, 0), (3, -2), 0, colors.black), 
                                ('LINEBEFORE', (4, 0), (4, -2), 0, colors.black), 
                                ('LINEBEFORE', (5, 0), (5, -2), 0, colors.black), 
                                ('LINEBEFORE', (6, 0), (6, -2), 0, colors.black), 
                                ('LINEAFTER', (6, 0), (6, -1), 0, colors.black), 
                                ('LINEBELOW', (0, -1), (-1, -1), 0, colors.black), 
                                ('LINEABOVE', (0, -1), (-1, -1), 0, colors.black), 
                                ])
            
            table.setStyle(style)

            all_tables.append(table)
            all_tables.append(Spacer(1, 3))
            semester_counter += 1
            if semester_counter == 6:
                all_tables.append(PageBreak())
            
        data1 = [['This is for signature only']]
        end_box = Table(data1, colWidths=[505], rowHeights=[50])
        style1 = TableStyle([ 
                            ('GRID', (0, 0), (-1, -1), 0, colors.black), 
                            ])
            
        end_box.setStyle(style1)
        all_tables.append(end_box)
        def draw_additional_content(canvas, doc):
            canvas.setFont("Times-Bold", 10)
            canvas.drawString(54, 561, "Name:")
            canvas.drawString(54, 547, "Registration No:")
            canvas.drawString(54, 534, "Program of Study:")
            canvas.drawString(54, 520, "Date of Issue:")
            canvas.drawString(294, 561, "Father Name:")
            canvas.drawString(294, 547, "Session:")
            canvas.drawString(294, 534, "Result Declaration Date:")

            canvas.setFont("Times-Roman", 10)
            canvas.drawString(150, 561, f"{student_name}")
            canvas.drawString(150, 547, f"UoL/CS-S-2019/25-BSCS")
            canvas.drawString(150, 534, f"{department}")
            canvas.drawString(150, 520, f"{issue_date}")
            canvas.drawString(410, 561, f"Ihsan Ullah")
            canvas.drawString(410, 547, f"2021-2025")
            canvas.drawString(410, 534, f"{result_date}")
            image_data = BytesIO(pic.read())
            image_data.seek(0)
            img = Image(image_data, width=0.815*inch, height=1*inch)  # Adjust the width and height as needed
            img.drawOn(canvas, 500, 516)
        # def sign(canvas, doc):
        #     canvas.draw        
        c.build(all_tables, onFirstPage=draw_additional_content)
        
        return response
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class SubjectsForThatSemester(ListView):
    template_name = 'SubjectsForThatSemester.html'
    model = SubjectAllocationModel
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        global subjects, student, semester
        student_id = self.request.session.get('student_id')
        student = Student.objects.get(id=student_id)
        semester_id = self.kwargs['semester_id']
        semester = Semester.objects.get(id=semester_id)
        subjects = SubjectAllocationModel.objects.filter(
                semester=semester,
                student=student
        )

        context['subjects'] = subjects
        return context

#Student As user Views

class Student_Dashboard(Student_Required_Mixin,TemplateView):
    template_name = 'student_user/student_dashboard.html'
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if hasattr(self.request.user, 'student'):
            student = self.request.user.student
            print(f'The Student is: {student}')
            subjects = SubjectAllocationModel.objects.filter(semester=student.student_semester, student=student)
            subject_count=subjects.count()
            context["subjects"] = subjects
            context["subject_count"] = subject_count
        return context

class StudentAttendanceSubjectsView(Student_Required_Mixin, ListView):
    model = SubjectAllocationModel
    template_name = "student_user/attendance_subjects.html"
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        student = self.request.user.student
        semester = student.student_semester
        subjects = SubjectAllocationModel.objects.filter(semester=student.student_semester)
        context['subjects'] = subjects
        context['semester'] = semester
        return context
    
class StudentAttendanceView(Student_Required_Mixin, ListView):
    model = SubjectAllocationModel
    template_name = "student_user/student_attendance.html"
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        student = self.request.user.student
        semester = student.student_semester
        subject_id = self.kwargs['subject_id']
        subject = SubjectAllocationModel.objects.get(id=subject_id)
        subject_name = subject.subject
        attendances = AttendenceReport.objects.filter(attendence_id__attendence_department=student.student_department, attendence_id__attendence_semester=student.student_semester, attendence_id__attendence_subject=subject_name, 
        attendence_student=student)
        present_count = AttendenceReport.objects.filter(attendence_id__attendence_department=student.student_department, attendence_id__attendence_semester=student.student_semester, attendence_id__attendence_subject=subject_name, 
        attendence_student=student, 
        attendence_status='Present').count()
        absent_count = AttendenceReport.objects.filter(attendence_id__attendence_department=student.student_department, attendence_id__attendence_semester=student.student_semester, attendence_id__attendence_subject=subject_name, 
        attendence_student=student, 
        attendence_status='Absent').count()
        attendance_count = attendances.count()
        if attendance_count != 0:
            percentage = round((present_count/attendance_count)*100)
        else:
            percentage = 0
        context['present_count'] = present_count
        context['absent_count'] = absent_count
        context['semester'] = semester
        context['attendances'] = attendances
        context['percentage'] = percentage
        context['subject'] = subject_name
        return context
    
class StudentResultView(Student_Required_Mixin, ListView):
    model = Result
    template_name = "student_user/student_result_view.html"
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        student = self.request.user.student
        marks_visible = student.marks_visible
        student_semester = student.student_semester
        results = Result.objects.filter(student=student)
        context['results'] = results
        context['student'] = student
        context['marks_visible'] = marks_visible
        context['student_semester'] = student_semester
        return context

class StudentMarksSubjects(Student_Required_Mixin, ListView):
    template_name = 'student_user/marks_subject.html'
    model = SubjectAllocationModel
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        semester_id = self.kwargs['semester_id']
        semester = Semester.objects.get(id=semester_id)
        student = self.request.user.student
        subjects = SubjectAllocationModel.objects.filter(student=student, semester=semester)
        context['subjects'] = subjects
        return context
    
class StudentPaperMarks(Student_Required_Mixin, ListView):
    model = Result
    template_name = 'student_user/student_paper_marks.html'

    def get_object(self, queryset=None):
        semester = hasattr(self.request.user, 'student') and self.request.user.student.student_semester
        return get_object_or_404(Student, user=self.request.user, semester=semester, marks_visible=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.student
        student_semester = student.student_semester
        subject_id = self.kwargs['subject_id']
        subject = SubjectAllocationModel.objects.get(id=subject_id)
        subject_name = subject.subject
        subject_semester = subject.semester
        marks = student.marks_visible
        results = PaperResult.objects.filter(student=student, subject_allocation=subject_name)
        context['student_semester'] = student_semester
        context['subject_semester'] = subject_semester
        context['marks'] = marks
        context['results'] = results
        context['subject_name'] = subject_name
        return context
    


# ADMIN Views
class Admin_Dashboard(AdminRequiredMixin, TemplateView):
    template_name = 'admin_templates/admin_dashboard.html'
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        students = Student.objects.all().count()
        teachers = Teacher.objects.all().count()
        departments = Department.objects.all().count()
        context["students"] = students
        context["teachers"] = teachers
        context["departments"] = departments
        return context

class DepartmentsView(AdminRequiredMixin, ListView):
    model = Department
    template_name = 'admin_templates/departments.html'
    context_object_name = 'departments'
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        department_count = Department.objects.all().count()
        context['department_count'] = department_count
        return context
    

class DepartmentsAddView(AdminRequiredMixin, CreateView):
    model = Department
    form_class = DepartmentAddForm
    template_name = 'admin_templates/departmentAdd.html'
    context_object_name = 'department'
    success_url = reverse_lazy('uniapp:departments')
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        department_count = Department.objects.all().count()
        messages.success(self.request, 'Department is Added Successfully')
        context['department_count'] = department_count
        return context

class DepartmentsUpdateView(AdminRequiredMixin, UpdateView):
    model = Department
    form_class = DepartmentUpdateForm
    template_name = 'admin_templates/departmentUpdate.html'
    context_object_name = 'department'
    success_url = reverse_lazy('uniapp:departments')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        messages.success(self.request, 'Department is Update Successfully')
        return context
    
class DepartmentsDeleteView(AdminRequiredMixin, DeleteView):
    model = Department
    template_name = 'admin_templates/departmentDelete.html'
    success_url = reverse_lazy('uniapp:departments')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        messages.success(self.request, 'Department is Deleted Successfully')
        return context

class AdminSubjectCreateView(AdminRequiredMixin, CreateView):
    form_class = SubjectCreateForm
    template_name = 'admin_templates/adminSubjectCreate.html'
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        global department
        department_id = self.kwargs['department_id']
        department = Department.objects.get(id=department_id)
        form.instance.subject_department = department
        return form
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["department"] = department
        return context

    def get_success_url(self):
        messages.success(self.request, f'The Subject is Successully Added To {department}')
        return reverse_lazy('uniapp:adminSubjectCreate', args=[self.kwargs['department_id']])

class AdminSubjectListView(AdminRequiredMixin, ListView):
    model = Subject
    template_name = 'admin_templates/adminSubjectList.html'
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        department_id = self.kwargs['department_id']
        department = Department.objects.get(id=department_id)
        subjects = Subject.objects.filter(subject_department=department)
        subjects_count = subjects.count()
        context['subjects'] = subjects
        context['subjects_count'] = subjects_count
        return context

class SemestersView(AdminRequiredMixin, ListView):
    model = Semester
    template_name = 'admin_templates/semesters.html'
    context_object_name = 'semester'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        department_id = self.kwargs['department_id']
        department = Department.objects.get(id=department_id)
        semesters = Semester.objects.filter(department=department).exclude(semester='Graduate')
        context['semesters'] = semesters
        self.request.session['department_id'] = department_id
        return context
    
class SemesterAddView(AdminRequiredMixin, CreateView):
    model = Semester
    form_class = SemesterAddForm
    template_name = 'admin_templates/semesterAdd.html'
    success_url = reverse_lazy('uniapp:departments')
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        global department
        department_id = self.kwargs['department_id']
        department = Department.objects.get(id=department_id)
        kwargs['department'] = department
        return kwargs
    def form_valid(self, form):
        form.instance.department = department
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['department'] = department
        return context
    
    def get_success_url(self):
        messages.success(self.request, f'The Semester is Successully Added To {department}')
        return reverse_lazy('uniapp:semesterAdd', args=[self.kwargs['department_id']])

class AdminSubjectAllocationCreateView(AdminRequiredMixin, CreateView):
    form_class = AdminSubjectAllocationForm
    template_name = 'admin_templates/adminsubjectallocation.html'
    success_url = reverse_lazy('uniapp:subjectallocation')
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        global department
        department_id = self.request.session.get('department_id')
        department = Department.objects.get(id=department_id)
        form.fields['semester'].queryset = Semester.objects.filter(department=department).exclude(semester='Graduate')
        return form
    def form_valid(self, form):
        subject = form.cleaned_data['subject']
        teacher = form.cleaned_data['teacher']
        semester = form.cleaned_data['semester']
        existing_allocated_subjects = SubjectAllocationModel.objects.filter(teacher=teacher, subject=subject, semester=semester, department=department).exists()
        if not existing_allocated_subjects:
            allocation_teacher = SubjectAllocationModel(teacher=teacher, subject=subject, semester=semester, department=department)
            allocation_teacher.save()
        students_in_semester = Student.objects.filter(student_semester=semester, student_department=department)
        for student in students_in_semester:
            allocation_student = SubjectAllocationModel(semester=semester, subject=subject, student=student, department=department)
            allocation_student.save()
        messages.success(self.request, f'{subject} is Successully Allocated To {teacher.teacher_name}')
        return redirect(self.success_url)

class AdminAllocatedSubjectsListView(AdminRequiredMixin, ListView):
    model = SubjectAllocationModel
    template_name = 'admin_templates/adminAllocatedSubjectsList.html'
    success_url = reverse_lazy('uniapp:subjectallocation')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        semester_id = self.kwargs['semester_id']
        semester = Semester.objects.get(id=semester_id)
        department = semester.department
        subjects = SubjectAllocationModel.objects.filter(department=department, semester=semester).exclude(teacher=None)
        context['subjects'] = subjects
        context['semester'] = semester
        context['department'] = department

        return context

class AdminTeacherListView(AdminRequiredMixin, ListView):
    model = Teacher
    template_name = 'admin_templates/adminteacherlist.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        department_id = self.kwargs['department_id']
        department = Department.objects.get(id=department_id)
        teachers = Teacher.objects.filter(teacher_department=department)
        teacher_count = teachers.count()
        context['department'] = department
        context['teachers'] = teachers
        context['teacher_count'] = teacher_count
        return context

class AdminAllStudentListView(AdminRequiredMixin, ListView):
    model = Student
    template_name = 'adminallstudentlist.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        global students
        department_id = self.kwargs['department_id']
        department = Department.objects.get(id=department_id)
        students = Student.objects.filter(student_department=department).exclude(student_semester__semester='Graduate')
        my_search = AllStudentsFilter(self.request.GET, queryset=students)
        students = my_search.qs
        student_count = students.count()
        all_marks_visible = True
        marks_visible = {}
        for i in students:
            marks_visible= i.marks_visible
        context['marks_visible'] = marks_visible
        context['students'] = students
        context['department'] = department
        context['my_search'] = my_search
        context['student_count'] = student_count
        context['all_marks_visible'] = all_marks_visible
        
        return context

    def post(self, request, *args, **kwargs):
        student_id = request.POST.get('student_id')
        marks_visible = request.POST.get('marks_visible') == 'true'
        student = Student.objects.get(id=student_id)
        student.marks_visible = marks_visible
        student.save()
        if request.POST.get('selectAllCheckbox') == 'true':
            context['all_marks_visible'] = all(
            student.marks_visible for student in students
        )
        return JsonResponse({'success': True})


class AdminGraduateStudentsList(AdminRequiredMixin, ListView):
    model = Student
    template_name = 'admingraduatestudentslist.html'
    # paginate_by = 10
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        department_id = self.kwargs['department_id']
        department = Department.objects.get(id=department_id)
        graduate_students = Student.objects.filter(student_department=department, student_semester__semester='Graduate')
        count = graduate_students.count()
        search_filter = GraduatesFilter(self.request.GET, queryset=graduate_students)
        graduate_students = search_filter.qs
        context['graduate_students'] = graduate_students
        context['department'] = department
        context['count'] = count
        context['search_filter'] = search_filter
        return context