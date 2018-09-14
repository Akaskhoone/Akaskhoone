from django.core.paginator import Paginator, EmptyPage, InvalidPage


def error_data(__data__: dict = None, **errors):
    for data in errors.items():
        if not isinstance(data[1], list):
            errors.update({data[0]: [data[1]]})
    if __data__ and __data__.get("error"):
        for data in __data__.get("error").items():
            if isinstance(errors.get(data[0]), list):
                try:
                    errors.get(data[0]).extend(data[1])
                except:
                    pass
            else:
                errors.update({data[0]: data[1]})
    return {"error": errors}


def success_data(message: str):
    return {"success": str(message)}


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
