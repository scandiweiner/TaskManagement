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
        user: str,
        checkin_date: datetime.date,
        description: str,
    ):
        """
        Create task and check in for user
        if user doesn't exist - create one
        :param user:
        :param checkin_date:
        :param description:
        :return: Task
        :raises
            errors.UserAlreadyHasOpenTask
        """
        with transaction.atomic():
            user, created = User.objects.get_or_create(username=user)
            if not created:
                # user can checkin only one task at a time
                if Task.objects.filter(
                    user__username=user,
                    checkout_date__isnull=True,
                ).exists():
                    raise errors.UserAlreadyHasOpenTask

            try:
                task = Task.objects.create(
                    user=user,
                    checkin_date=checkin_date,
                    description=description,
                )
            except TypeError:
                raise TypeError
            except KeyError:
                raise KeyError

        return task

    @classmethod
    def checkout(
        cls,
        user: int,
        checkout_date: datetime.date,
    ):
        """
        checkout task for user

        :param user:
        :param checkout_date:
        :return: Task
        :raises:
            task.DoesNotExist
            errors.TaskWasCheckedOut
        """
        try:
            task = Task.objects.get(
                user__username=user,
                checkout_date__isnull=True,
            )
            if task.checkout_date is not None:
                raise errors.TaskWasCheckedOut

            task.checkout_date = checkout_date
            task.save(update_fields=['checkout_date'])
            return task
        except Task.DoesNotExist:
            raise Task.DoesNotExist

    def __str__(self):
        return f'{self.id} task {self.description}'
