from django.contrib import admin
from task.models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    fields = (
        'description',
        'user',
        'checkin_date',
        'checkout_date',
    )
