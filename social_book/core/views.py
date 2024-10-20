from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
# send the messages
from django.contrib import messages
from .models import Profile, Post, LikePost
from django.contrib.auth.decorators import login_required
# Create your views here.


#need login in to be able to see the home page
@login_required(login_url='signin')
def index(request):
    user_object =User.objects.get(username = request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    posts = Post.objects.all()
    return render(request, 'index.html', {'user_profile': user_profile, 'posts': posts})

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
                user_login = auth.authenticate(username=username, password= password)
                auth.login(request, user_login)
                
                #create a profile object for the new user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('settings')
                
                       
        else:
            messages.info(request, 'Password is not matched')
            return redirect('signup')
    else:
        return render(request, 'signup.html')
    
def signin(request):
    if request.method == "POST":
        username=request.POST['username']
        password=request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            #user does not exist
            messages.info(request, 'Credentials Invalid')
            return redirect('signin')
           
            
        
    else:
        return render(request, 'signin.html')

@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')

@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == "POST":
        # Check if an image was uploaded
        image = request.FILES.get('image', None)  # Use None if no image is uploaded
        
        # Get the other form data
        bio = request.POST.get('bio', user_profile.bio)  # Use the current bio if not provided
        location = request.POST.get('location', user_profile.location)  # Use current location if not provided

        # Update profile with new data
        if image:
            user_profile.profileimg = image  # Only update image if a new one was uploaded
        user_profile.bio = bio
        user_profile.location = location
        user_profile.save()

        # Redirect after saving changes
        return redirect('settings')
                   
    return render(request, 'setting.html', {'user_profile': user_profile})
    
@login_required(login_url='signin')   
def upload(request):
    if request.method == "POST":
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']
        new_post = Post.objects.create(user=user, image=image, caption = caption)
        new_post.save()
        return redirect('/')
    else:
        return redirect("/")
    
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')
    post = Post.objects.get(id=post_id)
    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()
    if (like_filter == None):
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.no_of_likes = post.no_of_likes + 1
        post.save()
        return redirect('/')
    else:
        like_filter.delete()
        post.no_of_likes = post.no_of_likes - 1
        post.save()
        return redirect('/')

def profile(request, pk):
    user_object = User.objects.get(username = pk)
    user_profile = Profile.objects.get(user=user_object)
    #number of posts that belong to the user
    user_posts = Post.objects.filter(user=pk)
    user_post_length = len(user_posts)
    
    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length
    }
    
    return render(request, "profile.html", context)
    
    
    