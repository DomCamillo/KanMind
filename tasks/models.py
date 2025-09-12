from django.db import models
#from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
User = get_user_model()
from boards.models import Column

# Create your models here.
STATUS_CHOICES = [
    ('to-do', 'To Do'),
    ('in-progress', 'In Progress'),
    ('review', 'Review'),
    ('done', 'Done'),
]

class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    column = models.ForeignKey(Column,related_name='tasks', on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(User, related_name='tasks_assigned',on_delete=models.SET_NULL, null=True, blank=True)
    reviewer = models.ForeignKey(User, related_name='tasks_to_review',on_delete=models.SET_NULL, null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=20,choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High')
        ],default='medium')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='to-do')
    def __str__(self):
        return self.title



class Comment (models.Model):
    task = models.ForeignKey(Task, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.task} {self.author}"
