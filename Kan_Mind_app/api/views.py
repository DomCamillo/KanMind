from rest_framework import generics
from Kan_Mind_app.models import Column, Task, Comment, Board, BoardUser
from .serializers import BoardSerializer ,BoardUserSerializer, ColumnSerializer, TasksSerializer, CommentSerializer


class BoardUserView(generics.ListCreateAPIView):
    queryset = BoardUser.objects.all()
    serializer_class = BoardUserSerializer


class BoardUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BoardUser.objects.all()
    serializer_class = BoardUserSerializer


class TaskView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TasksSerializer
    #permission_classes = []


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TasksSerializer
    #permission_classes = []


class BaordView(generics.ListCreateAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer

class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer


class ColumnView(generics.ListCreateAPIView):
    queryset = Column.objects.all()
    serializer_class = ColumnSerializer


class ColumnDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Column.objects.all()
    serializer_class = ColumnSerializer


class CommentView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


