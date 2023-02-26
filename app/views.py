from django.shortcuts import render, redirect, get_object_or_404
from .forms import CreateBlogForm
from django.template.defaultfilters import slugify
from django.contrib import messages
from .models import Blog, Category, Comments, Newsletter, Subscription
from account.models import User
from taggit.models import Tag, TaggedItem
from django.db.models import Count
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .utils import my_paginator
import logging
logger = logging.getLogger('main')

# Create your views here.
def home(request):
    logger.info("Inside home page view")
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
    logger.info("Returning from Home view")
    return render(request, 'app/home.html',context)

@login_required(login_url='login')
def dashboard(request):
    logger.info(f"Dashboard function called")
    
    if not request.user.is_creator:
        logger.info(f"{request.user.username} is not a creator")
        return redirect('update_profile')
    blogs = Blog.objects.filter(created_by=request.user).order_by('-created_at')
    views = 0
    likes = 0
    for blog in blogs:
        views += blog.views
        likes += blog.likes

    user = request.user
    context = {
        'blogs':blogs,
        'user':user,
        'views':views,
        'likes':likes,
    }
    logging.info('Rendering from dashboard function')
    return render(request,'app/dashboard.html',context)

@login_required(login_url='login')
def create_blog(request):
    logger.info('Create blog function called') 
    form = CreateBlogForm()
    if request.method=="POST":
        logger.info('POST request method called') 
        form = CreateBlogForm(request.POST,request.FILES)
        if form.is_valid():
            logger.info('CreateBlogForm is valid') 
            blog = form.save(commit=False)
            blog.slug = 'temp'
            blog.created_by = request.user
            blog.save()
            form.save_m2m()
            blog.slug = slugify(blog.title+"-"+str(blog.id))
            blog.save()
            user = request.user
            user.is_creator = True
            user.save()
            # Create Subscription Profile
            Subscription.objects.update_or_create(creator=request.user)
            logger.info('Subscription Profile for creator is now created') 
            messages.success(request,'Blog has been created successfully')
            logger.info('Blog created Successfully, and Redirecting to dashboard')
            return redirect('dashboard')
        else:
            logger.warning(f'CreateBlogForm data is not available. Current data in the form is {form}')
            logger.error(f'Form validation errors are: {form.errors}')
            print(form.errors)
            messages.error(request,'Please fill all details properly.')
    logger.info('Rendering from GET method to create_blog.html file')
    return render(request,'app/create_blog.html',{'form':form})

@login_required(login_url='login')
def statistics(request):
    logger.info('Inside Blog Statistics Page')
    blogs = Blog.objects.filter(created_by=request.user).order_by('-created_at')
    context = {
        'blogs':blogs,
    }
    logger.info('We got all statistics and rendering data on statistics.html file')
    return render(request,'app/statistics.html',context)

@login_required(login_url='login')
def all_bookmarked_blogs(request):
    logger.info('Inside all_bookmarked_blogs() method')
    blogs = request.user.bookmarked_blogs.all()
    context = {
        'blogs':blogs,
    }
    logger.info('Got all Bookmarked Blogs. Rendering data on bookmarked.html page.') 
    return render(request,'app/bookmarked.html',context)

@login_required(login_url='login')
def bookmark_blog(request,slug):
    logger.info(f'Going to bookmark the blog "{slug}"') 
    blog = Blog.objects.get(slug=slug)
    if blog.bookmarked_by.filter(username=request.user.username).exists():
        blog.bookmarked_by.remove(request.user)
        messages.success(request,f'You removed {blog.title} from bookmarked.')
    else:
        blog.bookmarked_by.add(request.user)
        messages.success(request,f'You bookmarked {blog.title} ')
    blog.views-=1
    blog.save()
    logger.info(f'Bookmarked the blog "{slug}". Redirecting to view blog page.') 
    return redirect(view_blog,slug=slug)

@login_required(login_url='login')
def edit_blog(request,slug):
    try:
        blog = Blog.objects.get(slug=slug,created_by=request.user)
        tag_names = ','.join([tag.name for tag in blog.tags.all()])
        logger.info(f'{request.user.username} is going to edit blog {blog.slug}')
    except:
        messages.error(request,'No Blog Found!')
        logger.error(f"Blog with slug {blog.slug} not found or this slug is not existing. Redirecting to dashboard")
        return redirect('dashboard')
    if request.method=="POST":
        form = CreateBlogForm(request.POST,request.FILES,instance=blog)
        logger.info(f"Got the data from POST method. Going to update blog with slug {blog.slug}")
        if form.is_valid():
            blog = form.save(commit=False)
            blog.slug = slugify(blog.title+"-"+str(blog.id))
            blog.save()
            form.save_m2m()
            messages.success(request,'Blog has been Updated successfully')
            logger.info('Blog has been Updated successfully. Redirecting to dashboard page.')
            return redirect('dashboard')
        else:
            logger.warning('Data coming from POST method is not valid. Need to fill all details properly.')
            messages.error(request,'Please fill all details properly.')
    context = {
        'form' : CreateBlogForm(instance=blog, initial={'tags': tag_names}),
        'image_name': str(blog.image).split('/')[-1]
    }
    logger.info('This is a GET method while updating/editing the blog')
    return render(request,'app/create_blog.html',context)

@login_required(login_url='login')
def delete_blog(request,slug):
    try:
        logger.info(f'{request.user.username} is going to deleted blog {slug}')
        Blog.objects.get(slug=slug,created_by=request.user).delete()
        if Blog.objects.filter(created_by=request.user).count() == 0:
            request.user.update(is_creator=False)
        messages.success(request, 'Blog has been deleted successfully')
        logger.info('{request.user.username} has successfully deleted blog {slug}. Redirecting to dashboard.')
        return redirect('dashboard')
    except:
        logger.warning(f'Blog {slug} not found. Redirecting to dashboard.')
        messages.error(request,'No Blog Found!')
        return redirect('dashboard')

@login_required(login_url='login')
def make_featured(request,slug):
    try:
        logger.info(f'Going to make blog {slug} featured')
        blog = Blog.objects.get(slug=slug, created_by=request.user)
        if blog.is_featured:
            blog.is_featured =False
            logger.info(f'Blog {slug} is marked as unfeatured')
            messages.success(request, f'Blog "{blog.title}" is marked as Un-Featured.')
        else:
            blog.is_featured = True
            logger.info(f'Blog {slug} is marked as featured')
            messages.success(request, f'Blog "{blog.title}" is marked as Featured.')
        blog.save()
    except:
        logger.warning('Blog {slug} is not available in the database. Cannot be marked as featured. ')
        messages.error(request,'Invalid Blog! Can not marked as featured.')
    logger.info(f'At make_featured redirecting to statistics page.')
    return redirect('statistics')

@login_required(login_url='login')
def like_blog(request,slug):
    blog = get_object_or_404(Blog,slug=slug)
    if blog.liked_by.filter(username=request.user.username).exists():
        blog.liked_by.remove(request.user)
        blog.likes-=1
        logger.info(f'Un-Liked Blog {slug}')
        messages.success(request,f'You un-liked {blog.title} ')
    else:
        blog.liked_by.add(request.user)
        blog.likes+=1
        logger.info(f'Liked Blog {slug}')
        messages.success(request,f'You Liked {blog.title} ')
    blog.views -= 1
    blog.save()
    logger.info('Liked Blog View called successfully')
    return redirect('view_blog',slug)


def view_blog(request,slug):
    blog = get_object_or_404(Blog,slug=slug)
    blog.views += 1
    blog.save()

    # Get Feed Content
    recent_blogs = Blog.objects.filter(created_by=blog.created_by).order_by('-created_at')[:3]
    related_blogs = Blog.objects.filter(created_by=blog.created_by).order_by('-created_at')[:3]
    top_blogs = Blog.objects.filter(created_by=blog.created_by).order_by('-views','-likes')[:3]
    top_tags = Tag.objects.annotate(num_times_used=Count('taggit_taggeditem_items')).order_by('-num_times_used')[:10]

    if request.user:
        is_bookmarked = blog.bookmarked_by.filter(username=request.user.username).exists()
        is_liked = blog.liked_by.filter(username=request.user.username).exists()
    else:
        is_bookmarked = False
        is_liked = False

    # get comments
    comments = Comments.objects.filter(blog=blog)

    # Save comment for blog
    if request.POST and request.user.id != None:
        print(request.user)
        comment = request.POST.get('comment')
        Comments.objects.get_or_create(user = request.user, blog=blog, comment=comment)
        messages.success(request, f'You have commented on {blog.title}')

    context={
        'blog':blog,
        'recent_blogs':recent_blogs,
        'related_blogs':related_blogs,
        'top_blogs':top_blogs,
        'top_tags':top_tags,
        'is_bookmarked':is_bookmarked,
        'is_liked':is_liked,
        'comments':comments,
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
    
    paginator = my_paginator(request,blog,6)
    blogs = paginator.get('page_obj')
    
    context = {
        'blogs':blogs,
        'category':categories,
    }
    context.update(paginator.get('context'))

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
    paginator = my_paginator(request,blogs,6)
    blogs = paginator.get('page_obj')
    context = {
        'heading':heading,
        'blogs':blogs,
    }
    context.update(paginator.get('context'))
    return render(request,'app/view_all.html',context)

def view_all_blogs_at_category(request,category_name,heading,sort_method):
    blogs = Blog.objects.filter(category__name=category_name).order_by(sort_method)
    paginator = my_paginator(request,blogs,6)
    blogs = paginator.get('page_obj')
    context = {
        'heading':heading+' in '+category_name,
        'blogs':blogs,
    }
    context.update(paginator.get('context'))
    return render(request,'app/view_all.html',context)

def view_all_blogs_by_tag(request,tag):
    blogs = Blog.objects.filter(tags__name=tag)
    paginator = my_paginator(request,blogs,6)
    blogs = paginator.get('page_obj')
    context = {
        'heading':'Blogs related to #'+tag,
        'blogs':blogs,
    }
    context.update(paginator.get('context'))
    return render(request,'app/view_all.html',context)

def view_all_blogs_by_author(request,author,sort_method):
    sort = ""
    if sort_method == 'Top Blogs':
        sort = '-views'
    elif sort_method == 'Most Liked':
        sort = '-likes'
    else:
        sort = '-created_at'
    blogs = Blog.objects.filter(created_by__username=author).order_by(sort)
    paginator = my_paginator(request,blogs,6)
    blogs = paginator.get('page_obj')
    context = {
        'heading':f'{author}\'s {sort_method}',
        'blogs':blogs,
    }
    context.update(paginator.get('context'))
    return render(request,'app/view_all.html',context)
#___________________________________________________________________________________
def subscribe(request): 
    if request.POST:
        email = request.POST.get('email')
        Newsletter.objects.create(email = email)
        messages.success(request,'Thanks For Subscribing to Blog-It 😊')
    else:
        messages.error(request, 'Please enter valid email address')
    return redirect('home')
    
def author_detail(request,username):
    user = get_object_or_404(User,username=username)
    subscription = get_object_or_404(Subscription,creator__username=username) # Get the Subscription object with creator equal to user A
    subscribers = subscription.subscribers.all() # Get all subscribers of this Subscription
    top_blogs = Blog.objects.filter(created_by=user).order_by('-views')
    most_liked = Blog.objects.filter(created_by=user).order_by('-likes')
    latest_blogs = Blog.objects.filter(created_by=user).order_by('-created_at')

    if request.user.is_authenticated:
        is_subscribed = request.user in subscribers
    else:
        is_subscribed = False

    context={
        'author':user,
        'subscribers':subscribers,
        'most_liked':most_liked,
        'top_blogs':top_blogs,
        'latest_blogs':latest_blogs,
        'is_subscribed':is_subscribed,
    }
    return render(request,'app/author.html',context)

def subscribe_creator(request,username):
    user = get_object_or_404(User,username=username)
    subscriptionOBJ = Subscription.objects.get(creator=user) # Get the Subscription object with creator equal to user A
    subscribers = subscriptionOBJ.subscribers.all() # Get all subscribers of this Subscription
    if request.user in subscribers:
        subscriptionOBJ.subscribers.remove(request.user)
        messages.success(request, "You have unsubscribed the Creator")
    else:
        if request.user.id != None:
            subscriptionOBJ.subscribers.add(request.user)
            messages.success(request, "You have subscribed the Creator")  
        else:
            messages.error(request, "Please login to subscribe to the Creator")  
    return redirect('author_detail',username)
    