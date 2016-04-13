from django.core.urlresolvers import reverse
from django.db.models import Q
from django.utils.decorators import method_decorator

from django_datatables_view.base_datatable_view import BaseDatatableView
from pytz import utc

from utils.decorators import team_decorators
from utils.tools import capitalize

from .models import Task, Invoice, Accrual, Pcc
import datetime as dt

@method_decorator(team_decorators, name='dispatch')
class TaskJson(BaseDatatableView):
    # The model we're going to show
    model = Task
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
    columns = ['task_no', 'authorize_commitment', 'authorize_expenditure', 'total_accrual',
               'total_pcc_amount', 'actual_expenditure', 'state__name', 'id']

    # Hide Columns
    hidden_columns = [ i for i, x in enumerate(columns) if x in
                       []
                       ]

    column_names = [x for x in capitalize(columns)]
    column_names[1] = 'A. Commitment'
    column_names[2] = 'A. Expenditure'
    column_names[4] = 'Total PCC Amount'
    column_names[-2] = 'Current Process'
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
            return '<a href="{1}?pk={0}" class="btn default btn-xs red-stripe">Edit</a>' \
                   '<a href="{2}?pk={0}" class="btn default btn-xs green-stripe">Invoices</a>' \
                   '<a href="{3}?pk={0}" class="btn default btn-xs yellow-stripe">Workflow</a>' \
                   '<a href="{4}?pk={0}" class="btn default btn-xs blue-stripe">Accrual</a>' \
                   '<a href="{5}?pk={0}" class="btn default btn-xs purple-stripe">PCC</a>' \
                .format(
                    row.id,
                    reverse('budget_mgt:add_edit_task'),
                    reverse('budget_mgt:summary_invoice'),
                    reverse('budget_mgt:task_workflow'),
                    reverse('budget_mgt:table_accrual'),
                    reverse('budget_mgt:table_pcc'),

            )

        elif column == 'total_accrual':
            status = 'danger' if row.is_overbook else 'info'
            icon = 'close' if row.is_overbook else 'check'
            val = getattr(row, column)
            return '<span class="label label-{2}"> <i class="icon-{1}"></i></span> {0:,.2f}'.format(val, icon, status)

        elif column == 'total_pcc_amount':
            status = 'danger' if not row.is_pcc_amount_ok else 'info'
            icon = 'close' if not row.is_pcc_amount_ok else 'check'
            val = getattr(row, column)
            return '<span class="label label-{2}"> <i class="icon-{1}"></i></span> {0:,.2f}'.format(val, icon, status)

        elif column == 'actual_expenditure':
            status = 'danger' if row.is_overrun else 'info'
            icon = 'close' if row.is_overrun else 'check'
            val = getattr(row, column)
            return '<span class="label label-{2}"> <i class="icon-{1}"></i></span> {0:,.2f}'.format(val, icon, status)

        elif column == 'authorize_commitment':
            val = getattr(row, column)
            return '{:,.2f}'.format(val)

        elif column == 'authorize_expenditure':
            val = getattr(row, column)
            return '{:,.2f}'.format(val)

        elif column == 'state__name':
            val = getattr(row, column)
            if row.state == "Work Completed without PCC" :
                if isinstance(row.state_date, dt.datetime):
                    duration = dt.datetime.now(tz=utc) - row.state_date
                    days = duration.days
                else:
                    days = 0
                label_color = 'info' if days > 0 else 'danger'
                return '<h4 class="badge badge-{2}">{1}</h4> {0}'.format(val, days, label_color)
            return getattr(row, column)

        elif column == 'overrun':
            return '<span class="label label-{}"> {} </span>'.\
                format(
                    'danger' if row.is_overrun else 'success',
                    row.is_overrun
                )

        else:
            return super(TaskJson, self).render_column(row, column)

    def filter_queryset(self, qs):
        """
        Change the default startswith filtering to contains
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
class InvoiceJson(BaseDatatableView):
    # The model we're going to show
    model = Invoice
    def get_initial_queryset(self):
        # pk here is the Contractor ID
        filter = self.request.GET.get('filter',None)

        # return queryset used as base for futher sorting/filtering
        # these are simply objects displayed in datatable
        # You should not filter data returned here by any filter values entered by user. This is because
        # we need some base queryset to count total number of records.
        if filter == 'all':
            return self.model.objects.all()

        return self.model.objects.filter(~Q(current_process='Completed')).all()

    # define the columns that will be returned
    columns = ['contractor.name', 'task.task_no', 'region', 'invoice_no', 'invoice_amount',
               'state__name', 'remarks', 'id']

    # Hide Columns
    hidden_columns = [ i for i, x in enumerate(columns) if x in
                       []
                       ]

    column_names = [x for x in capitalize(columns)]
    column_names[0] = 'Contractor Name'
    column_names[1] = 'Task Number'
    column_names[-3] = 'Current Process'
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

            return '<a href="{1}?pk={0}" class="btn default btn-xs red-stripe">Edit</a>' \
                   '<a href="{2}?pk={0}" class="btn default btn-xs blue-stripe">Workflow</a>' \
                .format(
                    row.id,
                    reverse('budget_mgt:add_edit_invoice'),
                    reverse('budget_mgt:invoice_workflow'),
            )

        elif column == 'task.task_no':
            status = 'danger' if row.task.is_overrun is True else 'info'
            icon = 'close' if row.task.is_overrun is True else 'check'
            value = row.task.task_no
            url = reverse('budget_mgt:summary_invoice') + '?pk=' + '{}'.format(row.task_id)
            return '<span class="label label-{2}"> <i class="icon-{1}"></i></span> <a href="{3}">{0}</a>'.format(value, icon, status, url)

        elif column == 'invoice_no':
            status = 'danger' if row.status == 'Reject' else 'info'
            icon = 'close' if row.status == 'Reject' else 'check'
            value = row.invoice_no
            return '<span class="label label-{2}"> <i class="icon-{1}"></i></span> {0}'.format(value, icon, status)

        elif column == 'invoice_amount':
            val = getattr(row, column)
            return '{:,.2f}'.format(val)

        else:
            return super(InvoiceJson, self).render_column(row, column)

    def filter_queryset(self, qs):
        """
        Change the default startswith filtering to contains
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
class AccrualJson(BaseDatatableView):
    # The model we're going to show
    model = Accrual
    def get_initial_queryset(self):
        # pk here is the Contractor ID
        pk = self.request.GET.get('pk',None)

        # return queryset used as base for futher sorting/filtering
        # these are simply objects displayed in datatable
        # You should not filter data returned here by any filter values entered by user. This is because
        # we need some base queryset to count total number of records.
        if pk is None:
            return self.model.objects.all()

        return self.model.objects.filter(task__pk=pk).all()


    # define the columns that will be returned
    columns = ['task.task_no', 'ref_no', 'amount', 'id']

    # Hide Columns
    hidden_columns = [ i for i, x in enumerate(columns) if x in
                       []
                       ]

    column_names = [x for x in capitalize(columns)]
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
        if column == 'amount':
            val = getattr(row, column)
            return '{0:,.2f}'.format(val)

        elif column == 'id':
            return '<a href="{1}?pk={0}" class="btn default btn-xs red-stripe">Edit</a>' \
                .format(
                    row.id,
                    reverse('budget_mgt:add_edit_accrual'),
            )

        else:
            return super(AccrualJson, self).render_column(row, column)

    def filter_queryset(self, qs):
        """
        Change the default startswith filtering to contains
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
class PccJson(BaseDatatableView):
    # The model we're going to show
    model = Pcc
    def get_initial_queryset(self):
        # pk here is the Contractor ID
        pk = self.request.GET.get('pk',None)

        # return queryset used as base for futher sorting/filtering
        # these are simply objects displayed in datatable
        # You should not filter data returned here by any filter values entered by user. This is because
        # we need some base queryset to count total number of records.
        if pk is None:
            return self.model.objects.all()

        return self.model.objects.filter(task__pk=pk).all()


    # define the columns that will be returned
    columns = ['task.task_no', 'ref_no', 'amount', 'id']

    # Hide Columns
    hidden_columns = [ i for i, x in enumerate(columns) if x in
                       []
                       ]

    column_names = [x for x in capitalize(columns)]
    column_names[0] = 'Task No'
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
        if column == 'amount':
            val = getattr(row, column)
            return '{0:,.2f}'.format(val)

        elif column == 'id':

            return '<a href="{1}?pk={0}" class="btn default btn-xs red-stripe">Edit</a>' \
                .format(
                    row.id,
                    reverse('budget_mgt:add_edit_pcc'),
            )

        else:
            return super(PccJson, self).render_column(row, column)

    def filter_queryset(self, qs):
        """
        Change the default startswith filtering to contains
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
