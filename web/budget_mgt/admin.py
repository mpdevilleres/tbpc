from django.contrib import admin

from .models import TaskProcess, Task, Accrual, AuthorizeCommitment, AuthorizeExpenditure, \
    Pcc, InvoiceProcess, Invoice

# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton
# class EmployeeInline(admin.StackedInline):
#     model = Employee
#     can_delete = False
#     verbose_name_plural = 'employee'
#
# # Define a new User admin
class TaskAdmin(admin.ModelAdmin):
    pass
#
# # Re-register UserAdmin
# admin.site.unregister(User)
# admin.site.register(User, EmployeeAdmin)

admin.site.register(Task, TaskAdmin)
