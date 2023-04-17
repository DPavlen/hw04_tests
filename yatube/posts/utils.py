from django.core.paginator import Paginator

#  Число страниц
COUNT_PAGES = 10


def PaginatorPosts(posts, request):
    paginator = Paginator(posts, COUNT_PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
