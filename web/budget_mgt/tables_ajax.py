from django.core.urlresolvers import reverse
from django.db.models import Q, F, When, Value, Case, DecimalField
from django.utils.decorators import method_decorator

from django_datatables_view.base_datatable_view import BaseDatatableView
from pytz import utc

from utils.decorators import team_decorators
from utils.tools import capitalize

from .models import Task, Invoice, Accrual, Pcc, AuthorizeExpenditure, AuthorizeCommitment
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
            return self.model.objects.annotate(remaining_accrual=F('total_accrual')-F('actual_expenditure'),
                                               task_progress=Case(When(total_authorize_expenditure=0, then=Value('0.00')),
                                                                  default=F('total_pcc_amount')/F('total_authorize_expenditure'),
                                                                  output_field=DecimalField(),
                                                                  )
                                               ).all()

        return self.model.objects.filter(contractor__pk=pk)


    # define the columns that will be returned
    columns = ['task_no', 'total_authorize_commitment', 'total_authorize_expenditure', 'finance_actual_expenditure',
               'total_accrual', 'total_pcc_amount', 'actual_expenditure', 'remaining_accrual', 'task_progress',
               'state__name', 'tags.name']

    # Hide Columns
    hidden_columns = []

    column_names = [x for x in capitalize(columns)]
    column_names[1] = 'A. Commitment'
    column_names[2] = 'A. Expenditure'
    column_names[3] = 'F. Expenditure'
    column_names[5] = 'Total PCC'
    column_names[-5] = 'Invoice Paid'
    column_names[-4] = 'Remaining Accrual'
    column_names[-3] = 'Payment Type'
    column_names[-2] = 'Current Process'
    column_names[-1] = 'Tags'
    # define column names that will be used in sorting
    # order is important and should be same as order of columns
    # displayed by datatables. For non sortable columns use empty
    # value like ''
    order_columns = columns

    # columns to be summed
    sum_columns = [1, 2, 3, 4, 5, 6, 7]

    # set max limit of records returned, this is used to protect our site if someone tries to attack our site
    # and make it return huge amount of data
    max_display_length = 500

    def render_column(self, row, column):
        # We want to render user as a custom column
        if column == 'task_no':
            val = getattr(row, column)
            return '<a target="_blank" href="{1}?pk={0}">{2}</a>' \
                .format(
                    row.id,
                    reverse('budget_mgt:add_edit_task'),
                    val
            )

        elif column == 'tags.name':
            html_label = '<span class="label bg-green-jungle">{}</span> '

            html_tags = ''.join(sorted([html_label.format(i.name) for i in row.tags.all()]))
            return html_tags

        elif column == 'remaining_accrual':
            val = getattr(row, column)
            return '<span>{:,.2f}</span>'.format(val)

        elif column == 'total_pcc_amount':
            val = getattr(row, column)

            status = 'danger' if not row.is_pcc_complete else 'info'
            icon = 'close' if not row.is_pcc_complete else 'check'
            html_indicator = '<span class="label label-{0}"> <i class="icon-{1}"></i></span>'.format(status, icon)
            html_val = '<a class="sum" target="_blank" href="{1}?pk={2}">{0:,.2f}</a>'.format(val,
                                                             reverse('budget_mgt:table_pcc'),
                                                             row.id)
            html = html_indicator + ' ' + html_val
            return html
        elif column == 'total_authorize_expenditure':
            val = getattr(row, column)

            status = 'danger' if not row.is_expenditure_within_commitment else 'info'
            icon = 'close' if not row.is_expenditure_within_commitment else 'check'
            html_indicator = '<span class="label label-{0}"> <i class="icon-{1}"></i></span>'.format(status, icon)
            html_val = '<a class="sum" target="_blank" href="{1}?pk={2}">{0:,.2f}</a>'.format(val,
                                                             reverse('budget_mgt:table_authorize_expenditure'),
                                                             row.id)
            html = html_indicator + ' ' + html_val
            return html

        elif column == 'total_accrual':
            val = getattr(row, column)

            status = 'danger' if row.is_overbook else 'info'
            icon = 'close' if row.is_overbook else 'check'
            html_indicator = '<span class="label label-{0}"> <i class="icon-{1}"></i></span>'.format(status, icon)
            html_val = '<a class="sum" target="_blank" href="{1}?pk={2}">{0:,.2f}</a>'.format(val,
                                                             reverse('budget_mgt:table_accrual'),
                                                             row.id)
            html = html_indicator + ' ' + html_val
            return html

        elif column == 'task_progress':
            val = getattr(row, column)
            invoice = row.invoice_set.order_by('-pk').first()
            if invoice is None:
                payment_type =  'No Invoice'
            else:
                payment_type =  invoice.payment_type

            status = 'danger' if not row.is_within_work_criteria else 'info'
            html_indicator = '<span class="label label-{0}">{1:.2%}</span>'.format(status, val)
            html_val = payment_type
            html = html_indicator + ' ' + html_val
            return html

        # elif column == 'total_pcc_amount':
        #     val = getattr(row, column)
        #     html_val = '<a target="_blank" href="{1}?pk={2}">{0:,.2f}</a>'.format(val,
        #                                                                           reverse('budget_mgt:table_pcc'),
        #                                                                           row.id,
        #                                                                           )
        #     html = html_val
        #     return html

        elif column == 'actual_expenditure':
            val = getattr(row, column)
            status = 'danger' if row.is_overrun else 'info'
            icon = 'close' if row.is_overrun else 'check'
            html_indicator = '<span class="label label-{0}"> <i class="icon-{1}"></i></span>'.format(status, icon)
            html_val = '<a target="_blank" href="{1}?pk={2}">{0:,.2f}</a>'.format(val,
                                                             reverse('budget_mgt:summary_invoice'),
                                                             row.id)
            html = html_indicator + ' ' +html_val
            return html

        elif column == 'total_authorize_commitment':
            val = getattr(row, column)
            html = '<a target="_blank" href="{1}?pk={2}">{0:,.2f}</a>'.format(val,
                                                             reverse('budget_mgt:table_authorize_commitment'),
                                                             row.id)
            return html

        elif column == 'state__name':
            val = getattr(row, column)
            html_val = '<a target="_blank" href="{1}?pk={2}">{0}</a>'.format(val,
                                                             reverse('budget_mgt:task_workflow'),
                                                             row.id)
            if row.state == "PCC to be Issued" :
                if isinstance(row.state_date, dt.datetime):
                    # results is negative
                    duration = row.state_date - dt.datetime.now(tz=utc)
                    days = 30 + duration.days
                else:
                    days = 0
                label_color = 'info' if days > 0 else 'danger'
                html_indicator = '<h4 class="badge badge-{1}">{0}</h4>'.format(days, label_color)
                return html_indicator + ' ' + html_val
            return html_val

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

        return self.model.objects.filter(~Q(state='Completed')).all()

    # define the columns that will be returned
    columns = ['contractor.name', 'task.task_no', 'region', 'invoice_no', 'invoice_amount',
               'state__name', 'status', 'reject_date']

    # Hide Columns
    hidden_columns = [ i for i, x in enumerate(columns) if x in
                       []
                       ]

    column_names = [x for x in capitalize(columns)]
    column_names[0] = 'Contractor Name'
    column_names[1] = 'Task Number'
    column_names[-3] = 'Current Process'

    # columns to be summed
    sum_columns = [4]

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

        if column == 'state__name':
            val = getattr(row, column)
            html_val = '<a target="_blank" href="{1}?pk={2}">{0}</a>'.format(val,
                                                             reverse('budget_mgt:invoice_workflow'),
                                                             row.id)
            return html_val

        elif column == 'task.task_no':
            status = 'danger' if row.task.is_overrun is True else 'info'
            icon = 'close' if row.task.is_overrun is True else 'check'
            value = row.task.task_no
            url = reverse('budget_mgt:summary_invoice') + '?pk=' + '{}'.format(row.task_id)
            return '<span class="label label-{2}"> <i class="icon-{1}"></i></span> <a target="_blank" href="{3}">{0}</a>'.format(value, icon, status, url)

        elif column == 'invoice_no':
            val = getattr(row, column)

            status = 'danger' if row.status == 'Reject' else 'info'
            icon = 'close' if row.status == 'Reject' else 'check'
            html_indicator = '<span class="label label-{0}"> <i class="icon-{1}"></i></span>'.format(status, icon)
            html_val = '<a target="_blank" href="{1}?pk={2}">{0}</a>'.format(val,
                                                             reverse('budget_mgt:add_edit_invoice'),
                                                             row.id)
            html = html_indicator + ' ' + html_val
            return html

        elif column == 'reject_date':
            val = getattr(row, column)
            if val:
                return '{0:%d-%b-%Y}'.format(val)
            return ""
        elif column == 'invoice_amount':
            val = getattr(row, column)
            return '<span>{:,.2f}</span>'.format(val)

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
    columns = ['task.task_no', 'accrual_date', 'ref_no', 'amount', 'id']

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

    # columns to be summed
    sum_columns = [3,]

    # define hidden columns


    # set max limit of records returned, this is used to protect our site if someone tries to attack our site
    # and make it return huge amount of data
    max_display_length = 500

    def render_column(self, row, column):
        # We want to render user as a custom column
        if column == 'amount':
            val = getattr(row, column)
            return '{0:,.2f}'.format(val)

        elif column == 'accrual_date':
            val = getattr(row, column)
            return '{0:%d-%b-%Y}'.format(val)

        elif column == 'id':
            return '<a target="_blank" href="{1}?pk={0}" class="btn default btn-xs red-stripe">Edit</a>' \
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
class AuthorizeExpenditureJson(BaseDatatableView):
    # The model we're going to show
    model = AuthorizeExpenditure
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
    columns = ['task.task_no', 'task_child', 'amount', 'date', 'id']

    # Hide Columns
    hidden_columns = [ i for i, x in enumerate(columns) if x in
                       []
                       ]

    column_names = [x for x in capitalize(columns)]
    column_names[0] = 'Task (Parent)'
    column_names[1] = 'Task (Child)'
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

        elif column == 'date':
            val = getattr(row, column)
            return '{0:%d-%b-%Y}'.format(val)

        elif column == 'id':

            return '<a target="_blank" href="{1}?pk={0}" class="btn default btn-xs red-stripe">Edit</a>' \
                .format(
                    row.id,
                    reverse('budget_mgt:add_edit_authorize_expenditure'),
            )

        else:
            return super(AuthorizeExpenditureJson, self).render_column(row, column)

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
class AuthorizeCommitmentJson(BaseDatatableView):
    # The model we're going to show
    model = AuthorizeCommitment
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
    columns = ['task.task_no', 'task_child', 'amount', 'date', 'id']

    # Hide Columns
    hidden_columns = [ i for i, x in enumerate(columns) if x in
                       []
                       ]

    column_names = [x for x in capitalize(columns)]
    column_names[0] = 'Task (Parent)'
    column_names[1] = 'Task (Child)'
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

        elif column == 'date':
            val = getattr(row, column)
            return '{0:%d-%b-%Y}'.format(val)

        elif column == 'id':

            return '<a target="_blank" href="{1}?pk={0}" class="btn default btn-xs red-stripe">Edit</a>' \
                .format(
                    row.id,
                    reverse('budget_mgt:add_edit_authorize_commitment'),
            )

        else:
            return super(AuthorizeCommitmentJson, self).render_column(row, column)

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
    columns = ['task.task_no', 'is_complete', 'pcc_date', 'ref_no', 'amount', 'file', 'id']

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

        elif column == 'pcc_date':
            val = getattr(row, column)
            return '{0:%d-%b-%Y}'.format(val)

        elif column == 'file':
            val = getattr(row, column)

            if bool(val):
                status = 'info' if bool(val) else 'danger'
                icon = 'check' if bool(val) else 'close'
                html_indicator = '<span class="label label-{0}"> <i class="icon-{1}"></i></span>'.format(status, icon)
                html_val = '<a target="_blank" href="{1}pcc/{2}">{0}</a>'.format(html_indicator,
                                                                 reverse('main:get_file'),
                                                                 row.id)

            else:
                status = 'danger'
                icon = 'close'
                html_indicator = '<span class="label label-{0}"> <i class="icon-{1}"></i></span>'.format(status, icon)
                html_val = html_indicator

            html = html_val

            return html

        elif column == 'id':

            return '<a target="_blank" href="{1}?pk={0}" class="btn default btn-xs red-stripe">Edit</a>' \
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
