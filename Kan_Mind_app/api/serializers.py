from rest_framework import serializers
from Kan_Mind_app.models import Board ,BoardUser, Column , Comment, Task


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ['title', 'created_at', 'owner']



class BoardUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardUser
        fields = ['user','board', 'role']


class ColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Column
        fields = ['board', 'title', 'position']



class TasksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields ='__all__'


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['task', 'author', 'content', 'created_at']