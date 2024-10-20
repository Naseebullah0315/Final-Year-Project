import django_filters
from accounts.models import *
from django_filters import CharFilter

class GraduatesFilter(django_filters.FilterSet):
    search_name = CharFilter(field_name='student_name', lookup_expr='icontains')

class AllStudentsFilter(django_filters.FilterSet):
    search_name = CharFilter(field_name='student_name', lookup_expr='icontains')
    
 