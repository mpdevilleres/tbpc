from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator
from django_datatables_view.base_datatable_view import BaseDatatableView
from contract_mgt.models import ContractorContact, Contractor
from utils.decorators import team_decorators
from utils.tools import capitalize


@method_decorator(team_decorators, name='dispatch')
class ContractorContactJson(BaseDatatableView):
    # The model we're going to show
    model = ContractorContact
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
    columns = ['name', 'contractor_id', 'position', 'eadd', 'mobile_no', 'office_no', 'id']

    column_names = [x for x in capitalize(columns)]
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
        if column == 'id':
            return '<a href="{0}{1}" class="btn default btn-xs red-stripe">Edit</a>'.format(
                reverse('contract_mgt:add_edit_contact'), row.id)
        else:
            return super(ContractorContactJson, self).render_column(row, column)


@method_decorator(team_decorators, name='dispatch')
class ContractorJson(BaseDatatableView):
    # The model we're going to show
    model = Contractor

    # define the columns that will be returned
    columns = ['name','short_hand', 'profile','remarks', 'id']

    column_names = [x for x in capitalize(columns)]
    column_names[-1] = 'Option'
    # define column names that will be used in sorting
    # order is important and should be same as order of columns
    # displayed by datatables. For non sortable columns use empty
    # value like ''
    order_columns = ['name', 'short_hand', 'profile','remarks', 'id']

    # set max limit of records returned, this is used to protect our site if someone tries to attack our site
    # and make it return huge amount of data
    max_display_length = 500

    def render_column(self, row, column):
        # We want to render user as a custom column
        if column == 'id':
            button_edit = '<a href="{0}{1}" class="btn default btn-xs red-stripe">Edit</a>'.format(
                reverse('contract_mgt:add_edit_contractor'), row.id)
            button_contacts = '<a href="{0}{1}" class="btn default btn-xs green-stripe">View Contacts</a>'.format(
                reverse('contract_mgt:table_contact'), row.id)
            return button_edit + button_contacts
        else:
            return super(ContractorJson, self).render_column(row, column)