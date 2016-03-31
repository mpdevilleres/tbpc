from _decimal import Decimal

from django.db.models import Sum

from budget_mgt.models import Task


def summarize_invoice(task_pk=None):
    if task_pk is None:
        expenditure_tasks = Task.objects.all()
    else:
        expenditure_tasks = Task.objects.filter(pk=task_pk)

    for task in expenditure_tasks:
        total_amount = task.invoice_set.all().aggregate(sum=Sum('capex_amount'))
        task.expenditure_actual = Decimal('0.00') if total_amount['sum']is None else total_amount['sum']
        task.overrun = False if task.expenditure_actual <= task.commitment_value else True
        task.save()