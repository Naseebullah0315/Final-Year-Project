
def my_context_processor(request):
    hod_check = request.session.get('show_allocated_subjects', False)
    return {'hod_check': hod_check}