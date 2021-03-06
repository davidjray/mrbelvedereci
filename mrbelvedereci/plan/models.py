from __future__ import unicode_literals
import re

from django.db import models
from django.urls import reverse

TRIGGER_TYPES = (
    ('manual', 'Manual'),
    ('commit', 'Commit'),
    ('tag', 'Tag'),
)

class Plan(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    repo = models.ForeignKey('repository.Repository', related_name="plans")
    type = models.CharField(max_length=8, choices=TRIGGER_TYPES)
    regex = models.CharField(max_length=255, null=True, blank=True)
    flows = models.CharField(max_length=255)
    org = models.CharField(max_length=255)
    context = models.CharField(max_length=255, null=True, blank=True)
    public = models.BooleanField(default=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name','repo__owner','repo__name', 'active', 'context']

    def get_absolute_url(self):
        return reverse('plan_detail', kwargs={'plan_id': self.id})

    def __unicode__(self):
        return u'[{}] {}'.format(self.repo.name, self.name)

    def check_push(self, push):
        run_build = False
        commit = None
        commit_message = None

        # Handle commit events
        if self.type == 'commit':
            # Check if the event was triggered by a commit
            if not push['ref'].startswith('refs/heads/'):
                return run_build, commit, commit_message
            branch = push['ref'][11:]

            # Check the branch against regex
            if not re.match(self.regex, branch):
                return run_build, commit, commit_message

            run_build = True
            commit = push['after']
            if commit == '0000000000000000000000000000000000000000':
                run_build = False
                commit = None
            return run_build, commit, commit_message

            for commit_info in push.get('commits',[]):
                if commit_info['id'] == commit:
                    commit_message = commit_info['message']
                    break
   
            # Skip build if commit message contains [ci skip] 
            if commit_message and '[ci skip]' in commit_message:
                run_build = False
                commit = None
            return run_build, commit, commit_message
                

        # Handle tag events
        elif self.type == 'tag':
            # Check if the event was triggered by a tag
            if not push['ref'].startswith('refs/tags/'):
                return run_build, commit, commit_message
            tag = push['ref'][10:]
            
            # Check the tag against regex
            if not re.match(self.regex, tag):
                return run_build, commit, commit_message
   
            if push['head_commit']:
                # Skip... for some reason a second push event is sent that has no 'before' but does have a head_commit 
                return run_build, commit, commit_message

            run_build = True
            commit = push['before']
            return run_build, commit, commit_message
    
        return run_build, commit, commit_message
