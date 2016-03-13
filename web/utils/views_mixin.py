
# Class Based View Mixins
from django.contrib import messages
from django.shortcuts import get_object_or_404, render

from utils.forms import populate_obj


class AddEditMixin(object):
    form_class = None
    model = None
    template_name = None
    success_redirect_link = None

    def get(self, request, *args, **kwargs):
        pk = kwargs.pop('pk', None)
        if pk is None:
            forms = self.form_class()

        else:
            record = get_object_or_404(self.model, pk=pk)
            forms = self.form_class(initial=record.__dict__)

        return render(request, self.template_name, {'forms': forms})

    def post(self, request, *args, **kwargs):
        pk = kwargs.pop('pk', None)
        if pk is None:
            record = self.model()
        else:
            record = get_object_or_404(self.model, pk=pk)

        form = self.form_class(request.POST)

        if form.is_valid():
            cleaned_data = form.clean()
            populate_obj(cleaned_data, record)
            record.save()

            messages.success(request, "Successfully Updated the Database")
            return self.success_redirect_link

        return render(request, self.template_name, {'forms': form})