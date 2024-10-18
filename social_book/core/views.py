from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
# send the messages
from django.contrib import messages
from .models import Profile

# Create your views here.

def index(request):
    return render(request, 'index.html')

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        
        print(username)
        if (password == password2):
            if (User.objects.filter(email=email).exists()):
                messages.info(request, 'Email Taken')
                return redirect('signup')
            elif (User.objects.filter(username=username).exists()):
                messages.info(request, 'Username Taken')
                return redirect('signup')
            #create new user
            else:
                user = User.objects.create_user(username=username, email = email, password=password)
                user.save()
                
                #log user in and redirect to setting page
                
                #create a profile object for the new user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('signup')
                
                
            
        else:
            messages.info(request, 'Password is not matched')
            return redirect('signup')
    else:
        return render(request, 'signup.html')
    