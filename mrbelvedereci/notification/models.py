from __future__ import unicode_literals

from django.db import models

# Create your models here.
class PlanNotification(models.Model):
    user = models.ForeignKey('users.User', related_name='plan_notifications')
    plan = models.ForeignKey('plan.Plan', related_name='notifications')
    on_success = models.BooleanField(default=False)
    on_fail = models.BooleanField(default=True)
    on_error = models.BooleanField(default=True)

class BranchNotification(models.Model):
    user = models.ForeignKey('users.User', related_name='branch_notifications')
    branch = models.ForeignKey('repository.Branch', related_name='notifications')
    on_success = models.BooleanField(default=False)
    on_fail = models.BooleanField(default=True)
    on_error = models.BooleanField(default=True)

class RepositoryNotification(models.Model):
    user = models.ForeignKey('users.User', related_name='repo_notifications')
    repo = models.ForeignKey('repository.Repository', related_name='notifications')
    on_success = models.BooleanField(default=False)
    on_fail = models.BooleanField(default=True)
    on_error = models.BooleanField(default=True)
