from django.core.paginator import Paginator

def my_paginator(request,obj,per_page=3):
    paginator = Paginator(obj, per_page) # Show 25 contacts per page.
    page_number = int(request.GET.get('page',1))
    page_obj = paginator.get_page(page_number)
    pages = range(1,page_obj.paginator.num_pages+1)

    context = {
        'current_page':page_number,
        'page_obj':page_obj,
        'pages':pages,
    }
    return {'page_obj':page_obj, 'context':context}