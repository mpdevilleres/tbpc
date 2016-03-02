import datetime as dt
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import render, redirect

from .forms import LoginForm, ChangePasswordForm
# Create your views here.
from user_mgt.models import Attendance
from user_mgt.tables_ajax import AttendanceJson


def _login(request):
    form = LoginForm(request.POST or None)
    if form.is_valid():

        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                request.session.set_expiry(0)
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
        messages.info(request, "Time-out Successful")
        return redirect('team_mgt:index_dashboard')

    messages.info(request, "Time-out Failed, You are already timed out or not time-in")
    return redirect('team_mgt:index_dashboard')

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
