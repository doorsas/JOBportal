from django.shortcuts import render



from django.shortcuts import render

def eor_dashboard(request):
    return render(request, 'eor/dashboard.html')