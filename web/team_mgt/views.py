from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect, get_object_or_404

from utils.forms import populate_obj
from utils.dashboard_summarizer import summarize_team_task, _get
import pandas as pd
from contract_mgt.models import Contractor
from .forms import TeamTaskForm, TeamTaskHistoryForm
from .tables_ajax import TeamTaskJson, TeamTaskSummaryJson

# Create your views here.
from .models import TeamTask, TeamTaskHistory
from utils.tools import group_sort_to_list

@login_required
def add_edit_team_task(request, pk=None):
    _form = TeamTaskForm
    _model = TeamTask
    if pk is None:
        record = _model()
        form = _form(request.POST or None)
    else:
        record = get_object_or_404(_model, pk=pk)
        form = _form(initial=record.get_initials())

    if request.method == 'POST':
        form = _form(request.POST)
        if form.is_valid():
            cleaned_data = form.clean()
            users = cleaned_data.pop('user')
            populate_obj(cleaned_data, record)
            record.save()

            user_list = []
            for element in users:
                user = User.objects.get(pk=int(element))
                user_list.append(user)
            record.user = user_list
            summarize_team_task(pk=record.id)
            messages.info(request, "Successfully Updated the Database")

            return redirect('team_mgt:table_team_task')

    context = {
        'forms' : form,
        'form_title': 'Team Task'
    }
    return render(request, 'default/add_form.html', context)

@login_required
def add_team_task_history(request, pk=None):
    _form = TeamTaskHistoryForm

    team_task = get_object_or_404(TeamTask, pk=pk)
    form = _form(request.POST or None)

    if request.method == 'POST':
        form = _form(request.POST)
        if form.is_valid():
            cleaned_data = form.clean()
            #record.save()
            team_task.teamtaskhistory_set.create(**cleaned_data)

            team_task.status = cleaned_data['status']
            team_task.save()
            summarize_team_task(pk=team_task.id)
            messages.info(request, "Successfully Updated the Database")

            return redirect(reverse('team_mgt:timeline') + pk)

    context = {
        'forms' : form,
        'form_title': 'Team Task'
    }
    return render(request, 'default/add_form.html', context)

@login_required
def edit_team_task_history(request, pk=None):
    _form = TeamTaskHistoryForm

    record = get_object_or_404(TeamTaskHistory, pk=pk)
    form = _form(initial=record.__dict__)

    if request.method == 'POST':
        form = _form(request.POST)
        if form.is_valid():
            cleaned_data = form.clean()
            populate_obj(cleaned_data,record)
            record.save()
            summarize_team_task(pk=record.team_task_id)

            messages.info(request, "Successfully Updated the Database")
            return redirect(reverse('team_mgt:timeline') + '%s' % record.team_task_id)

    context = {
        'forms' : form,
        'form_title': 'Team Task'
    }
    return render(request, 'default/add_form.html', context)

@login_required
def add_edit_document(request, pk=None):
    pass

@login_required
def table_team_task(request, pk=None):

    if pk is None:
        data_table_url = reverse('team_mgt:table_team_task_json')
    else:
        data_table_url = reverse('team_mgt:table_team_task_json') + pk

    context = {
        'table_title': 'Team Task',
        'columns': getattr(TeamTaskJson,'column_names'),
        'hidden_columns': getattr(TeamTaskJson,'hidden_columns'),
        'data_table_url': data_table_url,
        'add_record_link': reverse('team_mgt:add_edit_team_task'),
    }
    return render(request, 'default/datatable.html', context)

@login_required
def table_document(request):
    pass

# DASHBOARDS
@login_required
def index_dashboard(request):

    """

    :param all_flag:
    :return:

    models involve User, Contractor, TeamTask
    """
    list_grouped = {
        'Internal': [],
        'Vendor Relationship': []
    }
    counter = {
        'Internal': 0,
        'Vendor Relationship': 0
    }

    team_task = TeamTask.objects.filter(user__pk=request.user.id)
    df_team_task = pd.DataFrame.from_records(team_task.values())
    df_contractor = pd.DataFrame.from_records(Contractor.objects.all().values())

    if not df_team_task.empty:
        mg = pd.merge(df_team_task, df_contractor, left_on='contractor_id', right_on='id', how='left')
        mg['sorting_date'] = pd.to_datetime(mg['date_expected'])
        mg = mg.sort_values(['sorting_date','id_x'], ascending=False) # Sort by Date and by ID of tasks
        mg.rename(columns={'id_x': 'id'},
                  inplace=True)

    # Filter per user, and open status
        gp = mg.groupby('classification')
        for i in gp.groups:                                      # Make sure that no error will raise if only 1 or 2 is
                                                                 # active
            rset = gp.get_group(i)
            num_total = len(rset)
            num_active = len(rset[rset['status']!='Closed'])
            list_grouped[i] = rset[rset['status']!='Closed'].to_dict('record')
            counter[i] = (num_active,num_total)

    context = {
       'i_task_data': list_grouped['Internal'], #i_task,
       'v_task_data': list_grouped['Vendor Relationship'], #v_task,
       'i_counter': counter['Internal'], #counter
       'v_counter': counter['Vendor Relationship'] #counter
    }
    return render(request,
                  "team_mgt/index_dashboard.html",
                  context)

@login_required
def summary_dashboard(request):
    how = 'left'    # default merging how

    team_task = TeamTask.objects.all()
    df_team_task = pd.DataFrame.from_records(team_task.values())

    contractor = Contractor.objects.all()
    df_contractor = pd.DataFrame.from_records(contractor.values())

    df_team_task_open = df_team_task[df_team_task['status']!='Close']      # filter by status open
    mg = pd.merge(df_team_task_open, df_contractor, left_on='contractor_id', right_on='id', how=how)

    group_by_severity = df_team_task_open.groupby('severity')
    group_by_category = df_team_task_open.groupby('category')
    group_by_classification = df_team_task_open.groupby('classification')
    group_by_contractor = mg.groupby('name')

#    if pk is None:
    data_table_url = reverse('team_mgt:table_team_task_summary_json')
#    else:
#        data_table_url = reverse('team_mgt:table_team_task_json') + pk

    context = {
        'table_title': 'Team Task',
        'columns': getattr(TeamTaskSummaryJson,'column_names'),
        'data_table_url': data_table_url,
        'open': len(df_team_task[df_team_task['status']!='Close']),
        'closed': len(df_team_task[df_team_task['status']=='Close']),

        'by_contractor': ('Contractor', group_sort_to_list(group_by_contractor)),
        'by_severity': ('Severity', group_sort_to_list(group_by_severity)),
        'by_category': ('Category', group_sort_to_list(group_by_category)),
        'by_classification': ('Classification', group_sort_to_list(group_by_classification)),
    }


    return render(request, "team_mgt/summary_dashboard.html", context)

# MISC VIEWS
@login_required
def notify(request, pk=None):
    pass

@login_required
def timeline(request, pk=None):

    team_task = get_object_or_404(TeamTask, pk=pk)
    history = TeamTaskHistory.objects.filter(team_task__pk=pk)
    try:
        earliest = history.earliest('id')
    except:
        earliest = None

    context = {
        'record': team_task,
        'history': history,
        'last_history': earliest,
        'team_task_edit_link': reverse('team_mgt:add_edit_team_task'),
        'add_team_task_history_link': reverse('team_mgt:add_team_task_history')
    }
    return render(request, 'team_mgt/timeline.html', context)

@login_required
def get_reference_no(request):
    pass