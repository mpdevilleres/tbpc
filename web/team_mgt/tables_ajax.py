from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator
from django_datatables_view.base_datatable_view import BaseDatatableView
from team_mgt.models import TeamTask, TeamTaskSummaryDashboard
from utils.decorators import team_decorators
from utils.tools import capitalize

from django.db.models import Q

@method_decorator(team_decorators, name='dispatch')
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
    columns = ['contractor.name', 'contract_no', 'description', 'severity', 'status', 'user__username', 'id']

    # Hide Columns
    hidden_columns = [ i for i, x in enumerate(columns) if x in
                       []
                       ]

    column_names = [x for x in capitalize(columns)]
    column_names[0] = 'Contractor'
    column_names[-2] = 'Person/s in charge'
    column_names[-1] = 'Option'
    # define column names that will be used in sorting
    # order is important and should be same as order of columns
    # displayed by datatables. For non sortable columns use empty
    # value like ''
    order_columns = columns

    # define hidden columns


    # set max limit of records returned, this is used to protect our site if someone tries to attack our site
    # and make it return huge amount of data
    max_display_length = 500

    def render_column(self, row, column):
        # We want to render user as a custom column
        if column == 'id':
            return '<a href="{0}{2}" class="btn default btn-xs red-stripe">Edit</a>' \
                   '<a href="{1}{2}" class="btn default btn-xs green-stripe">Timeline</a>' \
                .format(
                reverse('team_mgt:add_edit_team_task'),
                reverse('team_mgt:timeline'),
                row.id)
        else:
            return super(TeamTaskJson, self).render_column(row, column)

    def filter_queryset(self, qs):
        """ If search['value'] is provided then filter all searchable columns using istartswith
        """
        if not self.pre_camel_case_notation:
            # get global search value
            search = self.request.GET.get('search[value]', None)
            col_data = self.extract_datatables_column_data()
            q = Q()
            for col_no, col in enumerate(col_data):
                # apply global search to all searchable columns
                if search and col['searchable']:
                    q |= Q(**{'{0}__contains'.format(self.columns[col_no].replace('.', '__')): search})

                # column specific filter
                if col['search.value']:
                    qs = qs.filter(**{'{0}__contains'.format(self.columns[col_no].replace('.', '__')): col['search.value']})
            qs = qs.filter(q)
        return qs


@method_decorator(team_decorators, name='dispatch')
class TeamTaskSummaryJson(BaseDatatableView):
    # The model we're going to show
    model = TeamTaskSummaryDashboard
    def get_initial_queryset(self):
        # pk here is the Contractor ID
        pk = self.kwargs.pop('pk',None)

        # return queryset used as base for futher sorting/filtering
        # these are simply objects displayed in datatable
        # You should not filter data returned here by any filter values entered by user. This is because
        # we need some base queryset to count total number of records.
        if pk is None:
            return self.model.objects.filter(Q(status='Open')).order_by('-date_action').all()

#        return self.model.objects.filter(contractor__pk=pk)

        return self.model.objects.filter(Q(status='Open') & Q(contractor__pk=pk))


    # define the columns that will be returned
    columns = ['contractor', 'contract_no', 'action_taken', 'date_action', 'team_task_id']

    column_names = [x for x in capitalize(columns)]
    column_names[0] = 'Contractor'
    column_names[-2] = 'Update Date'
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
        if column == 'team_task_id':
            return '<a href="{0}{2}" class="btn default btn-xs red-stripe">Edit</a>' \
                   '<a href="{1}{2}" class="btn default btn-xs green-stripe">Timeline</a>' \
                .format(
                reverse('team_mgt:add_edit_team_task'),
                reverse('team_mgt:timeline'),
                row.team_task_id)
        elif column == 'date_action':
            return row.date_action.strftime('%d-%m-%Y')
        else:
            return super(TeamTaskSummaryJson, self).render_column(row, column)