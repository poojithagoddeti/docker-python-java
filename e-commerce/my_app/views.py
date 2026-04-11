from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserRegistrationForm, PostForm
from django.contrib.auth import authenticate, login, logout
from .models import Post
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponse


def home(request):
    name='shirisha'
    nums=[1,2,3,4,5,6]
    context={'name':name ,'nums':nums}
    return render(request,'home.html',context)


def user_login(request):
    if request.method=='GET':
        return render(request,'login.html')
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        user = authenticate(request,username=username,password=password)

        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            error="invalid ..."
            return render(request,'login.html',{'error':error})
        
def user_logout(request):
    logout(request)
    return redirect('login')


def user_register(request):
    form=UserRegistrationForm() #empty form submission
    if request.method=='GET':
       return render(request,'register.html',{'form':form})
    if request.method=='POST': #form with data
        form=UserRegistrationForm(request.POST) 
        if form.is_valid():
            form.save() #creat user
            return redirect('login')
        else:
            return render(request,'register.html',{'form':form})
        


def posts(request):
    post_list=Post.objects.all().order_by('-updated_at')
    return render(request,'posts.html',{'post_list':post_list})

def read_post(request,post_id):
    post = Post.objects.get(pk=post_id)
    return render(request,'read_post.html',{'post':post})

@login_required(login_url='login')
def create_post(request):
    form=PostForm()
    if request.method == 'GET':
        return render (request, 'create_post.html',{'form':form})
    if request.method == 'POST':
        form = PostForm(request.POST,request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts')
        else:
            return render(request , 'create_post.html',{'form':form})
        
@login_required(login_url='login')
def update_post(request,post_id):
    try:
        post=Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return HttpResponse('Post not found')
    if request.user != post.author:
        return HttpResponse('You are not authorized to update this post')
    form=PostForm(instance=post) #pre-populate the form with existing post data
    if request.method=='GET':
        return render(request,'update-post.html',{'form':form})
    if request.method=='POST':
        form=PostForm(request.POST,request.FILES,instance=post) #update the existing post with new data
        if form.is_valid():
            post=form.save(commit=False) #create post object but not save to database
            post.updated_at=timezone.now() #set the updated_at field to the current timestamp
            post.save() #save the post to database
            return redirect('posts')
        else:
            return render(request,'update-post.html',{'form':form})
        
def delete_post(request,post_id):
    try:
        post=Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return HttpResponse('Post not found')
    if request.user != post.author:
        return HttpResponse('You are not authorized to delete this post')
    post.delete() #delete the post from database
    return redirect('posts')