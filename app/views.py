from django.shortcuts import render, redirect, get_object_or_404
from .forms import CreateBlogForm
from django.template.defaultfilters import slugify
from django.contrib import messages
from .models import Blog


# Create your views here.
def home(request):
    return render(request, 'app/home.html')

def dashboard(request):
    blogs = Blog.objects.filter(created_by=request.user)
    context = {
        'blogs':blogs,
    }
    return render(request,'app/dashboard.html',context)

def create_blog(request):
    form = CreateBlogForm()
    if request.method=="POST":
        form = CreateBlogForm(request.POST,request.FILES)
        if form.is_valid():
            title = form.cleaned_data['title']
            short_description = form.cleaned_data['short_description']
            long_description = form.cleaned_data['long_description']
            slug = 'temp'
            image = form.cleaned_data['image']
            blog = Blog.objects.create(title=title,short_description=short_description,long_description=long_description,created_by = request.user,slug=slug,image=image)
            blog.slug = slugify(blog.title+"-"+str(blog.id))
            blog.save()
            messages.success(request,'Blog has been created successfully')
            return redirect('dashboard')
        else:
            print(form.errors)
            messages.error(request,'Please fill all details properly.')
    return render(request,'app/create_blog.html',{'form':form})

def statistics(request):
    blogs = Blog.objects.filter(created_by=request.user)
    context = {
        'blogs':blogs,
    }
    return render(request,'app/statistics.html',context)

def edit_blog(request,slug):
    try:
        blog = Blog.objects.get(slug=slug,created_by=request.user)
    except:
        messages.error(request,'No Blog Found!')
        return redirect('dashboard')
    if request.method=="POST":
        form = CreateBlogForm(request.POST,request.FILES)
        if form.is_valid():
            blog.title = form.cleaned_data['title']
            blog.short_description = form.cleaned_data['short_description']
            blog.long_description = form.cleaned_data['long_description']
            blog.image = form.cleaned_data['image']
            blog.is_featured = form.cleaned_data['is_featured']
            blog.save()
            messages.success(request,'Blog has been Updated successfully')
            return redirect('dashboard')
        else:
            messages.error(request,'Please fill all details properly.')
    context = {
        'form' : CreateBlogForm(instance=blog),
        'image_name': str(blog.image).split('/')[-1]
    }
    return render(request,'app/create_blog.html',context)

def delete_blog(request,slug):
    try:
        Blog.objects.get(slug=slug,created_by=request.user).delete()
        messages.success(request, 'Blog has been deleted successfully')
        return redirect('statistics')
    except:
        messages.error(request,'No Blog Found!')
        return redirect('dashboard')

def make_featured(request,slug):
    try:
        blog = Blog.objects.get(slug=slug, created_by=request.user)
        if blog.is_featured:
            blog.is_featured =False
            messages.success(request, f'Blog "{blog.title}" is marked as Un-Featured.')
        else:
            blog.is_featured = True
            messages.success(request, f'Blog "{blog.title}" is marked as Featured.')
        blog.save()
    except:
        messages.error(request,'Invalid Blog! Can not marked as featured.')
    return redirect('statistics')