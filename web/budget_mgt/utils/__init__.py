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
        task.actual_expenditure = Decimal('0.00') if total_amount['sum']is None else total_amount['sum']
        task.save()

def summarize_accrual(task_pk=None):
    if task_pk is None:
        expenditure_tasks = Task.objects.all()
    else:
        expenditure_tasks = Task.objects.filter(pk=task_pk)

    for task in expenditure_tasks:
        total_amount = task.accrual_set.all().aggregate(sum=Sum('amount'))
        task.total_accrual = Decimal('0.00') if total_amount['sum']is None else total_amount['sum']
        task.save()
