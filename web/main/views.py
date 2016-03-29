from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


@login_required
def index(request):
    if request.user.is_staff:
        return redirect('team_mgt:index_dashboard')
    return redirect('section_kpi_mgt:dashboard_kpi')