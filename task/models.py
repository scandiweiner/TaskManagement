import datetime

from django.contrib.auth import get_user_model
from django.db import models, transaction

from . import errors

User = get_user_model()


class Task(models.Model):
    """
    Model to create a task for user, task can be assigned to a user
    once he does checkin.

    checkin_date: The date when the task was started
    checkout_date: The date when the task was finished
    description: The task description
    user: The user performing the task
    """
    checkin_date = models.DateTimeField(null=True, blank=True)
    checkout_date = models.DateTimeField(null=True, blank=True)
    description = models.CharField(max_length=200)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    @classmethod
    def checkin(
        cls,
        task_id: int,
        user_id: int,
        checkin_date: datetime.date,
    ):
        """
        Check in task for user
        :param task_id:
        :param user_id:
        :param checkin_date:
        :return: Task
        :raises
            errors.UserAlreadyHasOpenTask
        """
        with transaction.atomic():
            if Task.objects.filter(
                user_id=user_id,
                checkout_date__isnull=True,
            ).exists():
                raise errors.UserAlreadyHasOpenTask
            else:
                try:
                    task = Task.objects.get(
                        id=task_id,
                        user__isnull=True,
                    )
                    task.user_id = user_id
                    task.checkin_date = checkin_date
                    task.save(update_fields=['user_id', 'checkin_date'])
                except Task.DoesNotExist:
                    raise Task.DoesNotExist
                except errors.UserAlreadyHasOpenTask:
                    raise errors.UserAlreadyHasOpenTask
                except TypeError:
                    raise TypeError
                except KeyError:
                    raise KeyError

        return task

    @classmethod
    def checkout(
        cls,
        task_id: int,
        checkout_date: datetime.date,
    ):
        """
        checkout task for user

        :param task_id:
        :param checkout_date:
        :return: Task
        :raises:
            task.DoesNotExist
            errors.TaskWasCheckedOut
        """
        try:
            task = Task.objects.get(
                id=task_id,
                checkin_date__isnull=False
            )
            if task.checkout_date is not None:
                raise errors.TaskWasCheckedOut

            task.checkout_date = checkout_date
            task.save(update_fields=['checkout_date'])
            return task
        except Task.DoesNotExist:
            raise Task.DoesNotExist

    def __str__(self):
        return f'task {self.description}'
