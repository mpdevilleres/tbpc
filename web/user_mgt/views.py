import datetime as dt
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404

from .forms import LoginForm, ChangePasswordForm, ReasonForm
# Create your views here.
from user_mgt.models import Attendance, AttendanceSummary
from user_mgt.tables_ajax import AttendanceJson, AttendanceSummaryJson
#from utils.summarizer import summarize_attendance
from utils.forms import populate_obj
from utils.summarizer import summarize_attendance


def _login(request):
    form = LoginForm(request.POST or None)
    if form.is_valid():

        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                request.session.set_expiry(36000)
                return redirect('main:index')
            else:
                messages.warning(request, 'User is Inactive, Please Contact the Administrator')
        else:
            messages.warning(request, 'Invalid Username or Password')
    context = {
        "form" : form
    }
    return render(request, 'user_mgt/login.html', context)

@login_required
def _logout(request):
    logout(request)
    messages.warning(request, 'Logout Successful')
    return redirect('user_mgt:login')

@login_required
def _change_password(request):
    form = ChangePasswordForm(request.POST or None, user=request.user)

    if form.is_valid():
        old = form.cleaned_data.get('old_password')
        new = form.cleaned_data.get('new_password')

        if old == new:
            user = User.objects.get(id=request.user.id)
            user.set_password(new)
            user.save()
            messages.info(request, "Password Change Successful")
    context = {
        'forms': form
    }
    return render(request, 'user_mgt/change_password.html', context=context)


@login_required
def table_attendance(request):

    data_table_url = reverse('user_mgt:table_attendance_json') + '%s' % request.user.id

    context = {
        'table_title': 'Attendance',
        'columns': getattr(AttendanceJson,'column_names'),
        'data_table_url': data_table_url,
#        'add_record_link': reverse('team_mgt:add_edit_team_task'),
    }
    return render(request, 'default/datatable.html', context)


@login_required
def table_attendance_summary(request):
    # if request.user.id not in [1]:
    #     raise Http404("option must be valid")
    #
    data_table_url = reverse('user_mgt:table_attendance_summary_json') + '%s' % request.user.id

    context = {
        'table_title': 'Attendance',
        'columns': getattr(AttendanceSummaryJson,'column_names'),
        'data_table_url': data_table_url,
#        'add_record_link': reverse('team_mgt:add_edit_team_task'),
    }
    return render(request, 'default/datatable.html', context)

# For attendance Logic

@login_required
def sign_in(request):
    today = dt.datetime.utcnow()
    attendance = Attendance.objects.filter(Q(user__pk=request.user.id) & Q(date_day=today.date()))\
        .first()
    if attendance is None:
        attendance = Attendance()
        attendance.user_id = request.user.id
        attendance.date_day = today.date()
        attendance.date_time = today.time()
        attendance.in_or_out = 'in'
        attendance.offset = '-'
        attendance.reason_for_excess = '-'
        attendance.accepted = '-'
        attendance.reason_for_rejection = '-'
        attendance.save()

        summarize_attendance(date=today.date(), user_pk=request.user.id)

        messages.info(request, "Time-in Successful")
        return redirect('team_mgt:index_dashboard')

    messages.info(request, "Time-in Failed, Already Signed IN")
    return redirect('team_mgt:index_dashboard')


@login_required
def sign_out(request):
    today = dt.datetime.utcnow()
    attendance_in = Attendance.objects.filter(Q(user__pk=request.user.id) &
                                                   Q(date_day=today.date()) &
                                                   Q(in_or_out='in')).\
        first()
    attendance_out = Attendance.objects.filter(Q(user__pk=request.user.id) &
                                                   Q(date_day=today.date()) &
                                                   Q(in_or_out='out')).\
        first()
    if attendance_in is not None and attendance_out is None:
        attendance = Attendance()
        attendance.user = request.user
        attendance.date_day = today.date()
        attendance.date_time = today.time()
        attendance.in_or_out = 'out'
        attendance.offset = '-'
        attendance.reason_for_excess = '-'
        attendance.accepted = '-'
        attendance.reason_for_rejection = '-'
        attendance.save()

        summarize_attendance(date=today.date(), user_pk=request.user.id)

        messages.info(request, "Time-out Successful")
        return redirect('team_mgt:index_dashboard')

    messages.info(request, "Time-out Failed, You are already timed out or not time-in")
    return redirect('team_mgt:index_dashboard')


@login_required
def add_edit_attendance_reason(request, pk=None):
    _form = ReasonForm
    _model = Attendance
    if pk is None:
        record = _model()
        form = _form(request.POST or None)
    else:
        record = get_object_or_404(_model, pk=pk)
        form = _form(initial=record.__dict__)

    if request.method == 'POST':
        form = _form(request.POST)
        if form.is_valid():
            cleaned_data = form.clean()
            populate_obj(cleaned_data, record)
            record.save()

            summarize_attendance(date=record.date_day, user_pk=request.user.id)

            messages.info(request, "Successfully Updated the Database")

            return redirect('user_mgt:table_attendance')

    context = {
        'forms' : form,
        'form_title': 'Attendance'
    }
    return render(request, 'default/add_form.html', context)


@login_required
def attendance_acceptance(request, pk=None, option=None):
    if option is None or pk is None or request.user.id not in [1]:
        raise Http404("option must be valid")

    else:
        summary = AttendanceSummary.objects.filter(Q(pk=pk)).first()
        summary.accepted = 'Yes' if int(option) == 1 else 'No'
        summary.save()
        return redirect('user_mgt:table_attendance_summary')
