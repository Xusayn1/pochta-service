from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 20
    page_query_param = 'page'
    page_size_query_param = 'page_size'
    max_page_size = 100

    def __init__(self):
        super().__init__()
        self.page = None
        self.request = None

    def paginate_queryset(self, queryset, request, view=None):
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = Paginator(queryset, page_size)
        page_number = request.query_params.get(self.page_query_param, 1)

        try:
            self.page = paginator.page(page_number)
        except (PageNotAnInteger, EmptyPage):
            return None

        self.request = request
        return list(self.page)

    def get_paginated_response(self, data):
        if self.page is None:
            return {
                'pagination': {
                    'total_items': 0,
                    'total_pages': 0,
                    'current_page': 0,
                    'page_size': 0,
                    'next_page': None,
                    'prev_page': None,
                },
                'results': None
            }

        return {
            'pagination': {
                'total_items': self.page.paginator.count,
                'total_pages': self.page.paginator.num_pages,
                'current_page': self.page.number,
                'page_size': len(data),
                'next_page': self.page.next_page_number() if self.page.has_next() else None,
                'prev_page': self.page.previous_page_number() if self.page.has_previous() else None,
            },
            'results': data
        }