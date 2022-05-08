from functools import wraps

from rest_framework import status
from rest_framework.response import Response


def required_params(request_attr="query_params", params=None):
    """when we use the @required_params func, it will return the decorator func
    which params is wrapped by view_func
    """

    if params is None:
        params = []

    def decorator(view_func):
        @wraps(view_func)
        def _warpped_view(instance, request, *args, **kwargs):
            data = getattr(request, request_attr)
            missing_params = [param for param in params if param not in data]
            if missing_params:
                params_str = ",".join(missing_params)
                return Response(
                    {
                        "message": "Missing {} in request".format(params_str),
                        "success": False,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return view_func(instance, request, *args, **kwargs)

        return _warpped_view

    return decorator
