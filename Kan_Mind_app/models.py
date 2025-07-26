from django.db import models
from django.contrib.auth.models import User

class Board (models.Model):
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_baords")

    def __str__(self):
        return self.title





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
        return self.user



class Column (models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='columns')
    title = models.CharField(max_length=100)
    position = models.PositiveBigIntegerField(default=0)

    def __str__(self):
        return f"{self.title} ({self.baord.title})"




class Task (models.Model):
    column = models.ForeignKey(Column, related_name='tasks', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    position = models.PositiveBigIntegerField(default=0)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='assigned_tasks', null=True, blank=True)
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    urgency = models.CharField(max_length=15)

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
