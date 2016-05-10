import mimetypes
import os

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import redirect

from wsgiref.util import FileWrapper

from django.utils.encoding import smart_str

from project import settings


@login_required
def index(request):
    if request.user.is_staff:
        return redirect('team_mgt:index_dashboard')
    return redirect('section_kpi_mgt:dashboard_kpi')

@login_required
def file_get(request, model, pk):
    if model is None:
        raise Http404()

    if pk is None:
        raise Http404()

    if model == 'pcc':
        from budget_mgt.models import Pcc
        _model = Pcc
    else:
        _model = None

    full_path = _model.objects.filter(pk=pk).first().file.path
    path, filename = os.path.split(full_path)

    file_wrapper = FileWrapper( open(full_path, 'rb'))
    content_type = mimetypes.guess_type(full_path)[0]
    response = HttpResponse(file_wrapper, content_type=content_type)
    response['Content-Length'] = os.path.getsize(full_path)
    response['Content-Disposition'] = "attachment; filename=%s" % smart_str(filename)
    response['X-Sendfile']= smart_str(os.path.join(settings.MEDIA_ROOT, path, filename))
    return response
