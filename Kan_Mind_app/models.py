from django.db import models
#from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
User = get_user_model()

class Board (models.Model):
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_boards")

    def __str__(self):
        return self.title

    # def save(self, *args, **kwargs):
    #     is_new = self.pk is None
    #     super().save(*args, **kwargs)
    #     if is_new:

    #         for status in ['to-do', 'in-progress', 'review', 'done']:
    #             Column.objects.create(board=self, title=status)




class BoardUser(models.Model):

    ROLE_CHOICES = (
        ("owner", "Owner"),
        ("member", "Member"),
        ("reviewer", "Reviewer")
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="board_member")
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="members")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="member")

    def __str__(self):
        return str(self.user)



class Column (models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='columns')
    title = models.CharField(max_length=100)
    position = models.PositiveBigIntegerField(default=0)

    def __str__(self):
        return f"{self.title} ({self.board.title})"


STATUS_CHOICES = [
    ('to-do', 'To Do'),
    ('in-progress', 'In Progress'),
    ('review', 'Review'),
    ('done', 'Done'),
]

class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    column = models.ForeignKey('Column',related_name='tasks', on_delete=models.CASCADE)
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


















# Create your models here.
