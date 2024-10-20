from typing import Any, Optional
from django.contrib import admin
from . models import*
from import_export.admin import ImportExportModelAdmin
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Department)
admin.site.register(Country)
admin.site.register(Province)
admin.site.register(District)
admin.site.register(Semester)
admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(PaperResult)
admin.site.register(Result)
admin.site.register(Subject)
admin.site.register(Attendence)
admin.site.register(AttendenceReport)
admin.site.register(SubjectAllocationModel)

class SubjectAllocationAdmin(admin.ModelAdmin):
    list_display = SubjectAllocationModel.DisplayFields
    def get_form(self, request, obj=None, **kwargs):
        form =  super().get_form(request, obj,**kwargs)
        if obj:
            assignment_id = obj.id
            assignment = Assignment.objects.get(id=assignment_id)
            department = assignment.student.student_department
            form.base_fields['semester'].queryset = Semester.objects.filter(department=department)

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = Assignment.DisplayFields
    def get_form(self, request, obj=None, **kwargs):
        form =  super().get_form(request, obj,**kwargs)
        if obj:
            assignment_id = obj.id
            assignment = Assignment.objects.get(id=assignment_id)
            department = assignment.student.student_department
            form.base_fields['semester'].queryset = Semester.objects.filter(department=department)

        return form
@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = Quiz.DisplayFields
    def get_form(self, request, obj=None, **kwargs):
        form =  super().get_form(request, obj,**kwargs)
        if obj:
            quiz_id = obj.id
            quiz = Quiz.objects.get(id=quiz_id)
            department = quiz.student.student_department
            form.base_fields['semester'].queryset = Semester.objects.filter(department=department)

        return form
@admin.register(Presentation)
class PresentationAdmin(admin.ModelAdmin):
    list_display = Presentation.DisplayFields
    def get_form(self, request, obj=None, **kwargs):
        form =  super().get_form(request, obj,**kwargs)
        if obj:
            presentation_id = obj.id
            presentation = Presentation.objects.get(id=presentation_id)
            department = presentation.student.student_department
            form.base_fields['semester'].queryset = Semester.objects.filter(department=department)

        return form
@admin.register(Mid)
class MidAdmin(admin.ModelAdmin):
    list_display = Mid.DisplayFields
    def get_form(self, request, obj=None, **kwargs):
        form =  super().get_form(request, obj,**kwargs)
        if obj:
            mid_id = obj.id
            mid = Mid.objects.get(id=mid_id)
            department = mid.student.student_department
            form.base_fields['semester'].queryset = Semester.objects.filter(department=department)

        return form
@admin.register(Final)
class FinalAdmin(admin.ModelAdmin):
    list_display = Final.DisplayFields
    def get_form(self, request, obj=None, **kwargs):
        form =  super().get_form(request, obj,**kwargs)
        if obj:
            final_id = obj.id
            final = Final.objects.get(id=final_id)
            department = final.student.student_department
            form.base_fields['semester'].queryset = Semester.objects.filter(department=department)

        return form
    
# @admin.register(Student)
# class StudentAdmin(ImportExportModelAdmin):
#     list_display = Student.DisplayFields
#     def get_form(self, request, obj=None, **kwargs):
#         form =  super().get_form(request, obj,**kwargs)
#         if obj:
#             assignment_id = obj.id
#             student = Student.objects.get(id=assignment_id)
#             department = student.student_department
#             form.base_fields['student_semester'].queryset = Semester.objects.filter(department=department)
#         return form
