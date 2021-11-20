import json
from urllib.request import Request

from django.contrib.auth import get_user_model
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
)
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from task import errors
from task.models import Task

User = get_user_model()


def render_response(data, error):
    return json.dumps(
        {
            'data': data,
            'error': error
        },
        indent=4, sort_keys=True, default=str,
    )


@csrf_exempt
@require_http_methods(["POST"])
def checkin_view(request: Request, task_id: int) -> HttpResponse:
    """
    view to checkin tasks for user

    :raises:
        errors.UserAlreadyHasOpenTask
        Task.DoesNotExist
    """
    data = json.loads(request.body.decode('utf-8'))

    try:
        task = Task.checkin(
            task_id=task_id,
            user_id=data['user_id'],
            checkin_date=data['checkin_date'],
        )
        data = render_response(
            data=(
                f' Checkin: user: {task.user.username}, '
                f'task: {task.description}'
            ),
            error=None,
        )
    except errors.UserAlreadyHasOpenTask:
        return HttpResponseBadRequest(
            render_response(
                data=None,
                error=errors.USER_ALREADY_HAS_AN_OPEN_TASK,
            ),
            status=400,
        )
    except (KeyError, TypeError, Task.DoesNotExist):
        return HttpResponseBadRequest(
            render_response(
                data=None,
                error=errors.BAD_REQUEST,
            ),
            status=400,
        )

    return HttpResponse(
        data,
        content_type="application/json",
        status=200,
    )


@csrf_exempt
@require_http_methods(["POST"])
def checkout_view(request: Request, task_id: int) -> HttpResponse:
    """
    view to checkout tasks for user

    :raises:
        errors.TaskWasCheckedOut
        Task.DoesNotExist
    """
    data = json.loads(request.body.decode('utf-8'))

    try:
        task = Task.checkout(
            task_id=task_id,
            checkout_date=data['checkout_date'],
        )
        data = render_response(
            data=f'Checkout: user: {task.user.username}',
            error=None,
        )
    except errors.TaskWasCheckedOut:
        return HttpResponseBadRequest(
            render_response(
                data=None,
                error=errors.TASK_WAS_CHECKED_OUT,
            ),
            status=400,
        )
    except (KeyError, TypeError, Task.DoesNotExist):
        return HttpResponseBadRequest(
            render_response(
                data=None,
                error=errors.BAD_REQUEST,
            ),
            status=400,
        )

    return HttpResponse(
        data,
        content_type="application/json",
        status=200,
    )


@csrf_exempt
@require_http_methods(["GET"])
def report_view(request: Request) -> HttpResponse:
    """
    report of all tasks for all users
    """
    data = {}
    users = User.objects.all()
    for user in users.iterator():
        tasks = list(Task.objects.filter(
            user=user,
            checkout_date__isnull=False,
        ))
        if tasks:
            user_data = {
                user.username: [
                    f'{i.description}:'
                    f' {i.checkout_date.hour - i.checkin_date.hour} hours'
                    for i in tasks
                ]
            }
            data.update(user_data)

    return HttpResponse(
        json.dumps(data, indent=4, sort_keys=True, default=str),
        content_type="application/json",
        status=200,
    )
