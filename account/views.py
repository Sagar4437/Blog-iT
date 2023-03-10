from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import User
from .forms import UserForm, UpdateProfileForm
# Create your views here.
def register(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
    
            user = User.objects.create_user(first_name=first_name, last_name=last_name,username=username,password=password, email=email)
            user.is_active = True
            user.save()
            login(request,user)
            messages.success(request,'Your account has been register successfully')
            messages.success(request,"You are now logged in!")
        else:
            messages.error(request,'Invalid Information')
    return render(request,'account/register.html')

def login_view(request):    
    if request.user.is_authenticated:
        messages.warning(request,'You are already Logged In!')
        return redirect("home")
    if request.method == "POST":
        email = request.POST['email'] 
        password = request.POST['password'] 

        user = authenticate(email=email, password=password)
        if user is not None:
            login(request,user)
            messages.success(request,"You are now logged in!")
            print("Logged in")
            return redirect("home")
        else:
            messages.error(request,"Invalid Credentials")
            return redirect(login_view)
    else:
        return render(request,'account/login.html')

def logout_view(request):
    logout(request)
    messages.success(request,'You have been logged out successfully!')
    return render(request,'account/logout.html')

def update_profile(request):
    user = request.user
    form = UpdateProfileForm(instance=user)
    if request.POST:
        form = UpdateProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request,'Profile has been updated Successfully')
            return redirect('dashboard')
        else:
            messages.error(request, form.errors)
            return redirect('update_profile')
    context = {
        'form':form,
        'user':user,
    }
    return render(request,'account/update-profile.html',context)