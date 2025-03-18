from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages

def index(request):
    return render(request, 'index.html')

def home(request):
    return render(request, 'index.html')

@csrf_exempt
def loginaction(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None
        
        if user is not None:
            if not user.is_active:
                messages.error(request, 'Account not activated, contact admin.')
                return redirect('home')

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_superuser or user.is_staff:
                    return redirect('adminhomepage')
                    # return render(request, 'admin/adminhomepage.html')
                else:
                    return redirect('staffhomepage')
                    # return render(request, 'staff/staffhomepage.html')
            else:
                messages.error(request, 'Invalid username or password.')
                return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('home')
    else:
        return render(request, 'home')

def logout_view(request):
    logout(request)
    return redirect('home')
