from django.http import Http404
from functools import wraps


def team_login_required(f):
    @wraps(f)
    def _wrapped_func(request, *args, **kwargs):
        if request.user.employee.is_employee:
            return f(request, *args, **kwargs)
        raise Http404()
    return _wrapped_func
