from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

def user_signup(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password1 = request.POST.get("password1", "").strip()
        password2 = request.POST.get("password2", "").strip()

    #Basic validations
        if not username:
            messages.error(request, "Username is required.")
            return render(request, "auth/signup.html")
        if password1 != password2:
            messages.error(request, "passwords do not match")
            return render(request, "auth/signup.html")
        if len(password1) < 6:
            messages.error(request, "password must be at least 6 charcters")
            return render(request, "auth/signup.html")
    
        if User.objects.filter(username=username).exists():
            messages.error(request, "That username has been taken.")
            return render(request, "auth/signup.html")
    #create user
        user = User.objects.create_user(username=username, email=email, password=password1)
    #Auto login after signup
        login(request, user)
        return redirect('home')
    return render(request, "auth/signup.html")

def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method== "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "invalid username or password.")

    return render(request, "auth/login.html")
@login_required
def user_logout(request):
    logout(request)
    return redirect('login')
# Create your views here.
