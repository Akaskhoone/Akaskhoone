from django.core.paginator import Paginator, EmptyPage, InvalidPage


def get_paginated_data(data, page=None, limit=None, url=""):
    next_page, previous_page = None, None
    try:
        page = int(page) if page else 1
        limit = int(limit) if limit else 2
        data = Paginator(data, limit)
        data = data.page(page)
        if data.has_next():
            next_page = F"{url}&page={page+1}&limit={limit}"
        if data.has_previous():
            previous_page = F"{url}&page={page-1}&limit={limit}"
        data = list(data)
    except EmptyPage or InvalidPage:
        data = None
    return {"data": data, "next": next_page, "previous": previous_page}
