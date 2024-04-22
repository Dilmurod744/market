from celery.result import AsyncResult
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import logout
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import path, include

from apps.tasks import custom_task, send_to_email
# from apps.tasks import custom_task, send_to_email
from root.settings import STATIC_URL, STATIC_ROOT, MEDIA_URL, MEDIA_ROOT


def custom_logout(request):
    logout(request)
    return redirect('product_list')


def create_check_task(r):
    task_result = custom_task.delay()
    response = {
        'success': True,
        'msg': f'Task navbatga yuborildi taskId: {task_result.id}'
    }
    return JsonResponse(response)


def custom_check_task(r, task_id):
    result = AsyncResult(task_id).state
    response = {
        'success': result,
        'msg': ''
    }
    return JsonResponse(response)


def view_test(request):
    send_to_email.delay(['dilmurod.xolmatovrg@gmail.com'], 'botirjon')
    # send_to_email()
    return JsonResponse({'msg': 'msg'})


def trigger_error(request):
    division_by_zero = 1 / 0


urlpatterns = [
                  path('sentry-debug/', trigger_error),
                  path('test', view_test),
                  path('create', create_check_task),
                  path('check/<task_id>', custom_check_task),
                  path('admin/logout/', custom_logout),
                  path('admin/logout/', custom_logout),
                  path('admin/', admin.site.urls),
                  path('', include('apps.urls')),
                  path("__debug__/", include("debug_toolbar.urls"))
              ] + static(STATIC_URL, document_root=STATIC_ROOT) + static(MEDIA_URL, document_root=MEDIA_ROOT)
