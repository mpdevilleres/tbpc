from team_mgt.models import *
import datetime as dt
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
