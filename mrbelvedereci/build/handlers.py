from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from mrbelvedereci.build.models import Build
from mrbelvedereci.build.models import Rebuild
from mrbelvedereci.build.tasks import check_queued_build
from mrbelvedereci.build.tasks import set_github_status

@receiver(post_save, sender=Build)
def queue_build(sender, **kwargs):
    build = kwargs['instance']
    created = kwargs['created']
    if not created:
        return

    # Queue the pending status task
    res_status = set_github_status.delay(build.id)
    build.task_id_status_start = res_status.id

    # Queue the check build task
    res_check = check_queued_build.delay(build.id)
    build.task_id_check = res_check.id

    build.save()

@receiver(post_save, sender=Rebuild)
def queue_rebuild(sender, **kwargs):
    rebuild = kwargs['instance']
    created = kwargs['created']

    if not created:
        return

    build = rebuild.build

    if rebuild == build.current_rebuild:
        return

    build.current_rebuild = rebuild

    # Queue the pending status task
    res_status = set_github_status.delay(build.id)
    build.task_id_status_start = res_status.id

    # Queue the check build task
    res_check = check_queued_build.delay(build.id)
    build.task_id_check = res_check.id

    build.save()
