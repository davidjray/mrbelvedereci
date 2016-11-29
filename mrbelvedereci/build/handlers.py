from django.db.models.signals import post_save
from django.dispatch import receiver
from mrbelvedereci.build.models import Build
from mrbelvedereci.build.tasks import run_build

@receiver(post_save, sender=Build)
def create_repo_webhooks(sender, **kwargs):
    build = kwargs['instance']
    created = kwargs['created']
    if not created:
        continue

    # Queue the background job
    run_build(build.id)