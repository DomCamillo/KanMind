from rest_framework import generics
from Kan_Mind_app.models import Column, Task, Comment, Board, BoardUser
from .serializers import BoardSerializer ,BoardUserSerializer, ColumnSerializer, TasksSerializer, CommentSerializer, RegistrationSerializer
from rest_framework.generics import ListAPIView
from rest_framework import status, viewsets
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .permissions import isOwnerOrAdmin, isUserOrReadOnly ,isAdminForDeleteORPatchandReadOnly, isAdminOnly, isBoardUser ,isBaordAdmin

class BoardUserView(generics.ListCreateAPIView):
    queryset = BoardUser.objects.all()
    serializer_class = BoardUserSerializer
    permission_classes = [isUserOrReadOnly]

class BoardUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BoardUser.objects.all()
    serializer_class = BoardUserSerializer
    permission_classes = [isAdminForDeleteORPatchandReadOnly]

class ColumnView(generics.ListCreateAPIView):
    queryset = Column.objects.all()
    serializer_class = ColumnSerializer
    permission_classes = [isUserOrReadOnly]

class ColumnDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Column.objects.all()
    serializer_class = ColumnSerializer
    permission_classes = [isBoardUser]

    def get_queryset(self):
        return Column.objects.filter(board__boarduser__user=self.request.user)


class CommentView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [isUserOrReadOnly]

class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [isOwnerOrAdmin]



class LoginView(ObtainAuthToken):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        data = {}
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            data = {
                'token':token.key,
                'username' : user.username,
                'email': user.email,
            }
        else:
            data=serializer.errors
        return Response(data)


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            saved_accoun = serializer.save()
            token, created = Token.objects.get_or_create(user=saved_accoun)
            data = {
                'token':token.key,
                'username' : saved_accoun.username,
                'email': saved_accoun.email,
            }
        else:
            data=serializer.errors
        return Response(data)


class EmailCheckView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        exists = User.objects.filter(email=email).exists()
        return Response({'email_exists': exists})

class TasksReviewerView(generics.ListAPIView):
    serializer_class = TasksSerializer
    permission_classes = [isUserOrReadOnly]

    def get_queryset(self):
        return Task.objects.filter(reviewer=self.request.user)

class TaskViewSet(viewsets.ModelViewSet):
     queryset = Task.objects.all()
     serializer_class = TasksSerializer
     permission_classes = [isBoardUser]

     def get_queryset(self):
      user = self.request.user
      if user.is_authenticated:
        return Task.objects.filter(column__board__members__user=user)
      return Task.objects.none()


class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [isUserOrReadOnly & isBaordAdmin]

    def get_queryset(self):
        return Board.objects.filter(boarduser__user=self.request.user)

class TasksAssignedToMeView(ListAPIView):
    serializer_class = TasksSerializer
    permission_classes = [isUserOrReadOnly]

    def get_queryset(self):
       return Task.objects.filter(assigned_to=self.request.user)


