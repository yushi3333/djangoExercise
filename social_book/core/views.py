from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
# send the messages
from django.contrib import messages
from .models import Profile, Post, LikePost, FollowersCount, Comment
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from itertools import chain
import random



#need login in to be able to see the home page
@login_required(login_url='signin')
def index(request):
    
    user_object =User.objects.get(username = request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    
    # Get the list of users that the current user is following
    user_following_list=[]
    feed = []
    user_following = FollowersCount.objects.filter(follower=request.user.username)
    
    for users in user_following:
        user_following_list.append(users.user)
        
     # Include current user's username to show their own posts
    user_following_list.append(request.user.username)
        
    # Get posts from followed users and attach their profile data
    for usernames in user_following_list:
        feed_lists = Post.objects.filter(user__username=usernames)
        for post in feed_lists:
            post.profile = Profile.objects.get(user=post.user)
        
        feed.append(feed_lists)
    feed_list =list(chain(*feed))
        
    
    
    # user suggestion starts
    all_users = User.objects.all()
    user_following_all = []
    for user in user_following:
        user_list = User.objects.filter(username=user.user).first()
        if user_list:
            user_following_all.append(user_list)
        
    new_suggestions_list = [x for x in all_users if x not in user_following_all and x != request.user]
    
    current_user = User.objects.filter(username=request.user.username).first()
    final_suggestions_list = [x for x in new_suggestions_list if x != current_user]
    random.shuffle(final_suggestions_list)
    
    # Prepare profile suggestions
    username_profile = []
    username_profile_list = []
    
    for users in final_suggestions_list:
        username_profile.append(users.id)
        
    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user = ids)
        username_profile_list.append(profile_lists)
    suggestions_username_profile_list = list(chain(*username_profile_list))
        
    
    return render(request, 'index.html', {'user_profile': user_profile, 'posts': feed_list, 'suggestions_username_profile_list':suggestions_username_profile_list[:4]})

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
        user = request.user
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

def profile(request, username):
    user_object = User.objects.get(username = username)
    user_profile = Profile.objects.get(user=user_object)
    #number of posts that belong to the user
    user_posts = Post.objects.filter(user=user_object)
    user_post_length = len(user_posts)
    follower=request.user.username
    user = username
    if FollowersCount.objects.filter(follower=follow, user=user_object).first():

        button_text="Unfollow"
    else:
        button_text="follow"
    user_followers = len(FollowersCount.objects.filter(user=user_object))
    user_following = len(FollowersCount.objects.filter(follower=user_object))
    
    
    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'user_followers': user_followers,
        'user_following': user_following,
        'button_text':button_text,
    }
    
    return render(request, "profile.html", context)
    
    
    
def follow(request):
    if request.method == "POST":
        follower = request.POST['follower']
        user = request.POST['user']
        
        #check if the user follow the person
        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/'+user)
        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect('/profile/'+ user)
    else:
        return redirect('/')
    
    
def search(request):
    
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    
    #get the user object(username, images)
    if request.method == "POST":
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains=username)
        username_profile = []
        username_profile_list = []
        
        
        for users in username_object:
            username_profile.append(users.id)
        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user = ids)
            username_profile_list.append(profile_lists)
            
        username_profile_list = list(chain(*username_profile_list))
        
        
    return render(request, 'search.html', {'user_profile': user_profile, 'username_profile_list':username_profile_list })



@login_required(login_url='signin')
def add_comment(request, post_id):
    if request.method == "POST":
        content = request.POST.get('content')
        post = Post.objects.get(id=post_id)

        if content:
            Comment.objects.create(post=post, user=request.user, content=content)

        return redirect('/')

@login_required(login_url='signin')
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Ensure only the post owner can delete the post
    if post.user == request.user:
        post.delete()
        messages.success(request, "Post deleted successfully!")
    else:
        messages.error(request, "You are not authorized to delete this post!")

    return redirect('/')