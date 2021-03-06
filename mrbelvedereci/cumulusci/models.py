from __future__ import unicode_literals

import json
import os

from cumulusci.core.config import ScratchOrgConfig
from cumulusci.core.exceptions import ScratchOrgException
from django.db import models
from django.urls import reverse
from django.utils import timezone

class Org(models.Model):
    name = models.CharField(max_length=255)
    json = models.TextField()
    scratch = models.BooleanField(default=False)
    repo = models.ForeignKey('repository.Repository', related_name='orgs')

    class Meta:
        ordering = ['name', 'repo__owner', 'repo__name']

    def __unicode__(self):
        return '{}: {}'.format(self.repo.name, self.name)

    def get_absolute_url(self):
        return reverse('org_detail', kwargs={'org_id': self.id})
    
class ScratchOrgInstance(models.Model):
    org = models.ForeignKey('cumulusci.Org', related_name='instances')
    build = models.ForeignKey('build.Build', related_name='scratch_orgs', null=True, blank=True)
    username = models.CharField(max_length=255)
    sf_org_id = models.CharField(max_length=32)
    deleted = models.BooleanField(default=False)
    delete_error = models.TextField(null=True, blank=True)
    json = models.TextField()
    json_dx = models.TextField()
    time_created = models.DateTimeField(auto_now_add=True)
    time_deleted = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        if self.username:
            return self.username
        if self.sf_org_id:
            return self.sf_org_id
        return '{}: {}'.format(self.org, self.id)

    def get_absolute_url(self):
        return reverse('org_instance_detail', kwargs={'org_id': self.org.id, 'instance_id': self.id})
    
    def get_org_config(self):
        # Write the org json file to the filesystem for Salesforce DX to use
        dx_local_dir = os.path.join(os.path.expanduser('~'), '.local', '.appcloud')
        if not os.path.isdir(dx_local_dir):
             dx_local_dir = os.path.join(os.path.expanduser('~'), '.appcloud')
        f = open(os.path.join(dx_local_dir, '{}.json'.format(self.username)), 'w')
        f.write(self.json_dx)
        f.close()

        org_config = json.loads(self.json)

        return ScratchOrgConfig(org_config)

    def delete_org(self, org_config=None):
        if org_config is None:
            org_config = self.get_org_config()
        
        try:
            org_config.delete_org()
        except ScratchOrgException as e:
            self.delete_error = e.message
            self.deleted = False
            self.save()
            return

        self.time_deleted = timezone.now()
        self.deleted = True
        self.save()

class Service(models.Model):
    name = models.CharField(max_length=255)
    json = models.TextField()

    def __unicode__(self):
        return self.name
