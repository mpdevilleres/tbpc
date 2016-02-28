from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


@login_required
def index(request):
    return redirect('team_mgt:index_dashboard')
