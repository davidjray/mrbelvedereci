import os

import heroku3

from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.core.paginator import Paginator

from django.apps import apps
from ansi2html import Ansi2HTMLConverter

def paginate(build_list, request):
    page = request.GET.get('page')
    per_page = request.GET.get('per_page', '25')
    paginator = Paginator(build_list, int(per_page))
    try:
        builds = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        builds = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        builds = paginator.page(paginator.num_pages)
    return builds

def view_queryset(request, query=None):
    if not query:
        query = {}

    if not request.user.is_staff:
        query['plan__public'] = True

    Build = apps.get_model('build', 'Build')
    builds = Build.objects.all()
    if query:
        builds = builds.filter(**query)

    order_by = request.GET.get('order_by', '-time_queue')
    order_by = order_by.split(',')
    builds = builds.order_by(*order_by)

    builds = paginate(builds, request)
    return builds

def format_log(log):
    conv = Ansi2HTMLConverter(dark_bg=False, scheme='solarized')
    headers = conv.produce_headers()
    content = conv.convert(log, full=False)
    content = '<pre class="ansi2html-content">{}</pre>'.format(content)
    #content = '<div class="body_foreground body_background">{}</div>'.format(content)
    return headers + content

def restart_heroku_dyno():
    api_token = os.environ.get('HEROKU_API_TOKEN')
    app_name = os.environ.get('HEROKU_APP_NAME')
    dyno_name = os.environ.get('DYNO')
    this_dyno = None

    conn = heroku3.from_key(api_token)
    app = conn.apps()[app_name]
    
    for dyno in app.dynos():
        if dyno.name == dyno_name:
            this_dyno = dyno
            break

    this_dyno.restart()
