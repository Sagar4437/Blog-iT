from .models import Category

def get_categories(request):
    context = {
        'categories':Category.objects.all()
    }
    return context