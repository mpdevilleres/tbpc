from django.core.urlresolvers import reverse
from django_datatables_view.base_datatable_view import BaseDatatableView
from team_mgt.models import TeamTask
from utils.tools import capitalize

from .choices import *

class TeamTaskJson(BaseDatatableView):
    # The model we're going to show
    model = TeamTask
    def get_initial_queryset(self):
        # pk here is the Contractor ID
        pk = self.kwargs.pop('pk',None)

        # return queryset used as base for futher sorting/filtering
        # these are simply objects displayed in datatable
        # You should not filter data returned here by any filter values entered by user. This is because
        # we need some base queryset to count total number of records.
        if pk is None:
            return self.model.objects.all()

        return self.model.objects.filter(contractor__pk=pk)


    # define the columns that will be returned
    columns = ['contractor_id', 'contract_no', 'description', 'severity', 'status', 'id']

    column_names = [x for x in capitalize(columns)]
    column_names[0] = 'Contractor'
    column_names[-1] = 'Option'
    # define column names that will be used in sorting
    # order is important and should be same as order of columns
    # displayed by datatables. For non sortable columns use empty
    # value like ''
    order_columns = columns

    # set max limit of records returned, this is used to protect our site if someone tries to attack our site
    # and make it return huge amount of data
    max_display_length = 500

    def render_column(self, row, column):
        # We want to render user as a custom column
        if column == 'contractor_id':
            return row.contractor.name
        elif column == 'severity':
            return choices_severity[row.severity - 1][1]
        elif column == 'status':
            return choices_status[row.status - 1][1]
        elif column == 'id':

            return '<a href="{0}{2}" class="btn default btn-xs red-stripe">Edit</a>' \
                   '<a href="{1}{2}" class="btn default btn-xs green-stripe">Timeline</a>' \
                .format(
                reverse('team_mgt:add_edit_team_task'),
                reverse('team_mgt:timeline'),
                row.id)
        else:
            return super(TeamTaskJson, self).render_column(row, column)
