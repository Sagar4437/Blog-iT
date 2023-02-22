from django.shortcuts import render, redirect, get_object_or_404
from .forms import CreateBlogForm
from django.template.defaultfilters import slugify
from django.contrib import messages
from .models import Blog, Category
from account.models import User
from taggit.models import Tag, TaggedItem
from django.db.models import Count
from django.db.models import Q


# Create your views here.
def home(request):
    featured_blog = Blog.objects.filter(is_featured=True).order_by('-views','-likes')[:1]
    top_blogs = Blog.objects.all().order_by('-views','-likes')[:3]
    new_blogs = Blog.objects.all().order_by('-created_at','-views')[:3]

    # Get a queryset of all tags that are not used in any Blog instances
    unused_tags = Tag.objects.filter(blog__isnull=True)
    # Delete the unused tags from the database
    unused_tags.delete()

    context = {
        'featured_blog':featured_blog[0],
        'top_blogs':top_blogs,
        'new_blogs':new_blogs,
    }
    return render(request, 'app/home.html',context)

def dashboard(request):
    blogs = Blog.objects.filter(created_by=request.user).order_by('-created_at')
    views = 0
    likes = 0
    for blog in blogs:
        views += blog.views
        likes += blog.likes
    if request.user != None:
        user = request.user
    else:
        user = User.objects.get(username='Guest')
    context = {
        'blogs':blogs,
        'user':user,
        'views':views,
        'likes':likes,
    }
    return render(request,'app/dashboard.html',context)

def create_blog(request):
    form = CreateBlogForm()
    if request.method=="POST":
        form = CreateBlogForm(request.POST,request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.slug = 'temp'
            blog.created_by = request.user
            blog.save()
            form.save_m2m()
            blog.slug = slugify(blog.title+"-"+str(blog.id))
            blog.save()
            messages.success(request,'Blog has been created successfully')
            return redirect('dashboard')
        else:
            print(form.errors)
            messages.error(request,'Please fill all details properly.')
    return render(request,'app/create_blog.html',{'form':form})

def statistics(request):
    blogs = Blog.objects.filter(created_by=request.user).order_by('-created_at')
    context = {
        'blogs':blogs,
    }
    return render(request,'app/statistics.html',context)

def edit_blog(request,slug):
    try:
        blog = Blog.objects.get(slug=slug,created_by=request.user)
        tag_names = ','.join([tag.name for tag in blog.tags.all()])
    except:
        messages.error(request,'No Blog Found!')
        return redirect('dashboard')
    if request.method=="POST":
        form = CreateBlogForm(request.POST,request.FILES,instance=blog)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.slug = slugify(blog.title+"-"+str(blog.id))
            blog.save()
            form.save_m2m()
            messages.success(request,'Blog has been Updated successfully')
            return redirect('dashboard')
        else:
            messages.error(request,'Please fill all details properly.')
    context = {
        'form' : CreateBlogForm(instance=blog, initial={'tags': tag_names}),
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

def like_blog(request,slug):
    blog = get_object_or_404(Blog,slug=slug, created_by=request.user)
    blog.likes += 1
    blog.save()
    return redirect('view_blog',slug)

def view_blog(request,slug):
    blog = get_object_or_404(Blog,slug=slug, created_by=request.user)
    blog.views += 1
    blog.save()
    recent_blogs = Blog.objects.filter(created_by=blog.created_by).order_by('-created_at')[:3]
    related_blogs = Blog.objects.filter(created_by=blog.created_by).order_by('-created_at')[:3]
    top_blogs = Blog.objects.filter(created_by=blog.created_by).order_by('-views','-likes')[:3]
    top_tags = Tag.objects.annotate(num_times_used=Count('taggit_taggeditem_items')).order_by('-num_times_used')[:10]
    context={
        'blog':blog,
        'recent_blogs':recent_blogs,
        'related_blogs':related_blogs,
        'top_blogs':top_blogs,
        'top_tags':top_tags,
    }
    return render(request, 'app/blogdetails.html',context)


def about(request):
    return render(request,'app/about.html')

def all_blogs(request):
    blog = Blog.objects.all()
    categories = Category.objects.all()
    if request.POST:
        blog_name = request.POST.get('blog_name')
        author = request.POST.get('author')
        category = request.POST.get('category')
        tags = request.POST.get('tags')
        sort_by = request.POST.get('sort_by')
        sort_dir = request.POST.get('sort_dir')
        sort = sort_dir + sort_by.lower()
        blog = blog.order_by(sort)
        if blog_name != '':
            blog = blog.filter(Q(title__icontains=blog_name) | Q(long_description__icontains=blog_name) | Q(short_description__icontains=blog_name) )
        if author != '':
            blog = blog.filter(created_by__username__icontains=author)
        if category != 'all':
            blog = blog.filter(category__name=category)
        

    context = {
        'blogs':blog[:6],
        'category':categories,
    }

    return render(request,'app/allblogs.html',context)


def category_details(request,category_name):
    top_blogs = Blog.objects.filter(category__name=category_name).order_by('-views')
    new_blogs = Blog.objects.filter(category__name=category_name).order_by('created_at')
    most_liked = Blog.objects.filter(category__name=category_name).order_by('-likes')
    blog_top_tags = top_blogs.values('tags__name').annotate(count=Count('tags')).order_by('-count')
    blog_top_tags = list(blog_top_tags.values_list('tags__name', flat=True))[:10]
    other_top_tags = Tag.objects.annotate(num_times_used=Count('taggit_taggeditem_items')).order_by('-num_times_used')[:10]
    context = {
        'top_blogs':top_blogs,
        'new_blogs':new_blogs,
        'most_liked':most_liked,
        'category_name':category_name,
        'blog_top_tags':blog_top_tags,
        'other_top_tags':other_top_tags,
    }
    return render(request, 'app/categories.html',context)

def view_all_blogs(request,heading,sort_method):
    blogs = Blog.objects.all().order_by(sort_method)
    context = {
        'heading':heading,
        'blogs':blogs,
    }
    return render(request,'app/view_all.html',context)

def view_all_blogs_at_category(request,category_name,heading,sort_method):
    blogs = Blog.objects.filter(category__name=category_name).order_by(sort_method)
    context = {
        'heading':heading+' in '+category_name,
        'blogs':blogs,
    }
    return render(request,'app/view_all.html',context)

def view_all_blogs_by_tag(request,tag):
    blogs = Blog.objects.filter(tags__name=tag)
    context = {
        'heading':'Blogs related to #'+tag,
        'blogs':blogs,
    }
    return render(request,'app/view_all.html',context)