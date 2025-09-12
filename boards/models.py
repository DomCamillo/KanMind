from django.db import models
#from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
User = get_user_model()

STATUS_CHOICES = [
    ('to-do', 'To Do'),
    ('in-progress', 'In Progress'),
    ('review', 'Review'),
    ('done', 'Done'),
]

# Create your models here.
class Board (models.Model):
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_boards")

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
        return str(self.user)



class Column (models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='columns')
    title = models.CharField(max_length=100, choices=STATUS_CHOICES)
    position = models.PositiveBigIntegerField(default=0)

    def __str__(self):
        return f"{self.title} ({self.board.title})"
