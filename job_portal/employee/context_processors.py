def base_template(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'employee'):
            return {'base_template': 'base_employee.html'}
        elif hasattr(request.user, 'employer'):
            return {'base_template': 'base_employer.html'}
        elif hasattr(request.user, 'eor'):
            return {'base_template': 'base_eor.html'}
    return {'base_template': 'base.html'}