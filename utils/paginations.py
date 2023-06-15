from dateutil import parser
from django.conf import settings
from rest_framework.pagination import BasePagination
from rest_framework.response import Response


class EndlessPagination(BasePagination):
    page_size = 20 if not settings.TESTING_MODE else 10

    def __init__(self):
        super().__init__()
        self.has_next_page = False

    def to_html(self):
        pass

    def paginate_ordered_list(self, reversed_order_list, request):
        if "created_at__gt" in request.query_params:
            created_at__gt = parser.isoparse(request.query_params["created_at__gt"])
            objects = []
            for obj in reversed_order_list:
                if obj.created_at > created_at__gt:
                    objects.append(obj)
                else:
                    break
            self.has_next_page = False
            return objects

        index = 0
        if "created_at__lt" in request.query_params:
            created_at__lt = parser.isoparse(request.query_params["created_at__lt"])
            for index, obj in enumerate(reversed_order_list):
                if obj.created_at < created_at__lt:
                    break
            else:
                reversed_order_list = []
        self.has_next_page = len(reversed_order_list) > index + self.page_size
        return reversed_order_list[index : index + self.page_size]

    def paginate_queryset(self, queryset, request, view=None):
        if type(queryset) == list:
            return self.paginate_ordered_list(queryset, request)

        # (gt=greater than)
        if "created_at__gt" in request.query_params:
            created_at__gt = request.query_params["created_at__gt"]
            queryset = queryset.filter(created_at__gt=created_at__gt)
            self.has_next_page = False
            return queryset.order_by("-created_at")

        # (lt=less than)
        if "created_at__lt" in request.query_params:
            created_at__lt = request.query_params["created_at__lt"]
            queryset = queryset.filter(created_at__lt=created_at__lt)

        queryset = queryset.order_by("-created_at")[: self.page_size + 1]
        self.has_next_page = len(queryset) > self.page_size
        return queryset[: self.page_size]

    def paginate_cached_list(self, cached_list, request):
        paginated_list = self.paginate_ordered_list(cached_list, request)
        if "created_at__gt" in request.query_params:
            return paginated_list
        if self.has_next_page:
            return paginated_list
        if len(cached_list) < settings.REDIS_LIST_LENGTH_LIMIT:
            return paginated_list
        return None

    def get_paginated_response(self, data):
        return Response(
            {
                "has_next_page": self.has_next_page,
                "results": data,
            }
        )
