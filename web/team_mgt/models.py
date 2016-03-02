from django.contrib.auth.models import User
from django.db import models
from contract_mgt.models import Contractor
from utils.models import TimeStampedBaseModel, ManytoManyMixin


# Create your models here.


class TeamTask(ManytoManyMixin, TimeStampedBaseModel):

    team_task_no = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    contract_no = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    severity = models.CharField(max_length=100)
    end_user = models.CharField(max_length=100)
    remarks = models.TextField(blank=True)
    date_expected = models.DateTimeField(blank=True, null=True)
    date_team_task = models.DateTimeField(blank=True, null=True)
    date_close = models.DateTimeField(blank=True, null=True)
    classification = models.CharField(max_length=100)
    notify = models.PositiveIntegerField(default=0)

    contractor = models.ForeignKey(Contractor, on_delete=models.CASCADE)
    user = models.ManyToManyField(User)

    def __str__(self):
        return "%s" % (self.team_task_no)

    @property
    def choice_alias(self):
        return (self.id, self.team_task_no)

    @property
    def user_names(self):
        return '; '.join([i.username for i in self.user.all()])


class TeamTaskHistory(TimeStampedBaseModel):

    team_task = models.ForeignKey(TeamTask, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    action_taken = models.TextField(blank=True)
    next_action = models.TextField(blank=True)
    remarks = models.TextField(blank=True)
    status = models.CharField(max_length=100)
    date_expected = models.DateTimeField(blank=True, null=True)
    date_action = models.DateTimeField(blank=True, null=True)


class TeamTaskSummaryDashboard(TimeStampedBaseModel):

    team_task_id = models.PositiveIntegerField(default=0)
    contractor = models.CharField(max_length=100, null=True)
    contract_no = models.CharField(max_length=100, null=True)
    action_taken = models.TextField(blank=True)
    date_action = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=100)
