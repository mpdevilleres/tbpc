# Create your views here.
from django.http import Http404, HttpResponse
from django.views.generic import View

# class Workflow(object):
#     model = None
#     def __init__(self, model=None):
#         self.model = model
#
#     @classmethod
#     def get_urls(cls):
#         from django.conf.urls import url
#
#         urlpatterns = [
#             url(r'^next-process/$', cls.NextProcessView.as_view(), name='next_process'),
#             url(r'^update-workflow/$', cls.NextProcessView.as_view(), name='update_workflow'),
#             url(r'^process/$', cls.NextProcessView.as_view(), name='process'),
#             url(r'^workflow/$', cls.NextProcessView.as_view(), name='workflow'),
#         ]
#         return urlpatterns

class NextProcessView(View):
    model = None
    process = None
    def get(self, request, *args, **kwargs):
        # main model pk
        pk = request.GET.get('pk', None)

        if pk is None:
            raise Http404()

        record = self.model.objects.filter(pk=pk).first()
        process_order = self.process.objects.values_list('pk', flat=True).order_by('order')
        current_workflow = record.workflow_set.filter(status=False).order_by('pk').first()
    
        return HttpResponse(request.GET.get('a',''))

    def post(self, request, *args, **kwargs):
        raise Http404()

class WorkflowUpdateView(View):

    def get(self, request, *args, **kwargs):
        return HttpResponse('Working')

    def post(self, request, *args, **kwargs):
        raise Http404()

class AddEditProcessView(View):

    def get(self, request, *args, **kwargs):
        return HttpResponse('Working')

    def post(self, request, *args, **kwargs):
        raise Http404()

class EditWorkflowView(View):

    def get(self, request, *args, **kwargs):
        return HttpResponse('Working')

    def post(self, request, *args, **kwargs):
        raise Http404()
