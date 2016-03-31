from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator
from django_datatables_view.base_datatable_view import BaseDatatableView
from user_mgt.models import AttendanceSummary, Attendance
from utils.decorators import team_decorators
import datetime as dt

from utils.tools import capitalize

@method_decorator(team_decorators, name='dispatch')
class AttendanceJson(BaseDatatableView):
    # The model we're going to show
    model = Attendance
    def get_initial_queryset(self):
        # pk here is the Contractor ID
        pk = self.kwargs.pop('pk',None)

        # return queryset used as base for futher sorting/filtering
        # these are simply objects displayed in datatable
        # You should not filter data returned here by any filter values entered by user. This is because
        # we need some base queryset to count total number of records.

        return self.model.objects.filter(user__pk=pk)


    # define the columns that will be returned
    columns = ['date_day', 'date_time', 'in_or_out', 'reason_for_excess', 'id']

    column_names = [x for x in capitalize(columns)]
    column_names[0] = 'Date'
    column_names[1] = 'Time'
    column_names[2] = 'In or Out'
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
        if column == 'id' and row.in_or_out == 'out':
            return '<a href="{}{}" class="btn default btn-xs blue-stripe">Add/Edit Reason</a>' \
                .format(
                reverse('user_mgt:add_edit_attendance_reason'),
                row.id)
        elif column in ['id', 'reason_for_excess'] and row.in_or_out == 'in':
            return 'N/A'
        elif column == 'date_time':
            # timedelta of 4 because users are in UAE and server uses utc
            time = dt.datetime.combine(dt.date.today(), row.date_time)  + dt.timedelta(hours=4)
            return time.strftime('%H:%M')
        else:
            return super(AttendanceJson, self).render_column(row, column)


@method_decorator(team_decorators, name='dispatch')
class AttendanceSummaryJson(BaseDatatableView):
    # The model we're going to show
    model = AttendanceSummary
    def get_initial_queryset(self):
        # pk here is the Contractor ID
        pk = self.kwargs.pop('pk',None)

        # return queryset used as base for futher sorting/filtering
        # these are simply objects displayed in datatable
        # You should not filter data returned here by any filter values entered by user. This is because
        # we need some base queryset to count total number of records.

        return self.model.objects.filter(user__pk=pk)


    # define the columns that will be returned
    columns = ['user.username', 'date_day', 'date_time_in', 'date_time_out', 'total_hours',
               'reason_for_excess', 'accepted', 'id']

    column_names = [x for x in capitalize(columns)]
    column_names[0] = 'employee'
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
        if column == 'id':
            return '<a href="{0}{1}/1" class="btn default btn-xs green-stripe">Accept</a>' \
                   '<a href="{0}{1}/0" class="btn default btn-xs red-stripe">Reject</a>' \
                .format(
                reverse('user_mgt:acceptance'),
                row.id)
        elif column in ['date_time_in', 'date_time_out']:
            # timedelta of 4 because users are in UAE and server uses utc
            time = dt.datetime.combine(dt.date.today(), getattr(row,column))  + dt.timedelta(hours=4)
            return time.strftime('%H:%M')
        elif column == 'total_hours':
            return int(row.total_hours)
        else:
            return super(AttendanceSummaryJson, self).render_column(row, column)
