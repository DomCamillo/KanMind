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





# class TaskView(generics.ListCreateAPIView):
#     queryset = Task.objects.all()
#     serializer_class = TasksSerializer
#     #permission_classes = []


# class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Task.objects.all()
#     serializer_class = TasksSerializer
#     #permission_classes = []


# class BoardView(generics.ListCreateAPIView):
#     queryset = Board.objects.all()
#     serializer_class = BoardSerializer

# class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Board.objects.all()
#     serializer_class = BoardSerializer




class BoardUserView(generics.ListCreateAPIView):
    queryset = BoardUser.objects.all()
    serializer_class = BoardUserSerializer


class BoardUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BoardUser.objects.all()
    serializer_class = BoardUserSerializer

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


class RegistrationView(APIView):                   # APi view fuer eigene Logik (z. B. Passwort-Check, Token-Erstellung), individuelle Antworten, kein automatisches Speichern
    permission_classes = [AllowAny]                # damit auch nicht eingeloggte nutzer sich registrieren koennen

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        data = {}                      # leeres dictionary wo entwerder ein error oder die user daten gespeichert
        if serializer.is_valid():
            saved_accoun = serializer.save()               # serializer.save() nicht aufrufst, wird der User nicht erstellt, und du kannst auch keinen Token erzeugen.
            token, created = Token.objects.get_or_create(user=saved_accoun) # erstellt einen token oder prueft ob der user schon eine hat
            data = {                            # wenn die daten validiert wurden (is_valid) dann werden die userdaten (data) zurueck gesendet
                'token':token.key,
                'username' : saved_accoun.username,
                'email': saved_accoun.email,
            }
        else:
            data=serializer.errors
        return Response(data)


class EmailCheckView(APIView):
    def post(self, request):
        email = request.data.get('email')
        exists = User.objects.filter(email=email).exists()
        return Response({'email_exists': exists})

class TasksReviewerView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TasksSerializer

class TaskViewSet(viewsets.ModelViewSet):
     queryset = Task.objects.all()
     serializer_class = TasksSerializer


class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer

class TasksAssignedToMeView(ListAPIView):
    serializer_class = TasksSerializer

    def get_queryset(self):
       return Task.objects.filter(assigned_to=self.request.user)


