import datetime as dt

from django.db.models import Q

from team_mgt.models import *
from user_mgt.models import Attendance, AttendanceSummary


def _get(val, attr, default=None):
    try:
        return getattr(val, attr)
    except:
        return default

def summarize_team_task(pk=None):
    if pk is None:
        team_tasks = TeamTask.objects.all()
    else:
        team_tasks = TeamTask.objects.filter(pk=pk)

    for task in team_tasks:
        history = task.teamtaskhistory_set.order_by('-pk').first()

        summary = TeamTaskSummaryDashboard.objects.filter(team_task_id=task.id).first()
        if summary is None:
            summary = TeamTaskSummaryDashboard()

        summary.team_task_id = task.id

        summary.contractor = task.contractor.name
        summary.contract_no = task.contract_no
        summary.status = task.status

        summary.action_taken = _get(history, 'action_taken', '')
        summary.date_action = _get(history, 'date_action', dt.datetime(1990,1,1))

        summary.save()

def summarize_attendance(date=None, user_pk=None):

    summary = AttendanceSummary.objects.filter(Q(user__pk=user_pk) & Q(date_day=date)).first()
    if summary is None:
        summary = AttendanceSummary()

    attendance = Attendance.objects.filter(Q(user__pk=user_pk) & Q(date_day=date)).all()

    if len(attendance) == 2:
        time_in = attendance.filter(Q(in_or_out='in')).first().date_time
        time_out = attendance.filter(Q(in_or_out='out')).first().date_time
        hours = time_out.hour - time_in.hour
        mins = time_out.minute - time_in.minute
        total_hours = hours + (mins/60)

        summary.date_day = attendance.first().date_day
        summary.date_time_in = time_in
        summary.date_time_out = time_out
        summary.total_hours = total_hours
        summary.reason_for_excess = attendance.filter(Q(in_or_out='out')).first().reason_for_excess

        summary.save()

    else:
        return "Attendance Requires Time in and Time out"

    return 'Summary success'

