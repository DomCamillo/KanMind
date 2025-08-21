from rest_framework import generics
from Kan_Mind_app.models import Column, Task, Comment, Board, BoardUser
from .serializers import BoardSerializer ,BoardUserSerializer, ColumnSerializer, TasksSerializer, CommentSerializer, RegistrationSerializer
from rest_framework.generics import ListAPIView
from rest_framework import status, viewsets
from Kan_Mind_app.models import STATUS_CHOICES
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
#from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny ,IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import NotAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from .permissions import isOwnerOrAdmin, isUserOrReadOnly ,IsAdminForCrud, isAdminOnly, isBoardUser ,isBaordAdmin, isCommentAuthorOrAdmin

class BoardUserView(generics.ListCreateAPIView):
    queryset = BoardUser.objects.all()
    serializer_class = BoardUserSerializer
    permission_classes = [ IsAuthenticated]

class BoardUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BoardUser.objects.all()
    serializer_class = BoardUserSerializer
    permission_classes = [ IsAuthenticated]

class ColumnView(generics.ListCreateAPIView):
    queryset = Column.objects.all()
    serializer_class = ColumnSerializer
    permission_classes = [ IsAuthenticated]

class ColumnDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Column.objects.all()
    serializer_class = ColumnSerializer
    permission_classes = [ IsAuthenticated]

    def get_queryset(self):
        return Column.objects.filter(board__members__user=self.request.user)



class CommentView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        task_id = self.kwargs.get('task_pk')  # task_pk aus URL
        return Comment.objects.filter(task_id=task_id).order_by('-created_at')  # Neueste zuerst

    def perform_create(self, serializer):
        task_id = self.kwargs.get('task_pk')

        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound("Task not found.")

        user = self.request.user
        if not BoardUser.objects.filter(board=task.column.board, user=user).exists():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You are not a member of this board.")


        serializer.save(task=task, author=user)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        task_id = self.kwargs.get('task_pk')
        return Comment.objects.filter(task_id=task_id)

    def get_object(self):
        comment = super().get_object()
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            if comment.author != self.request.user:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("You can only edit/delete your own comments.")
        return comment






class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Invalid email or password"}, status=400)
        auth_user = authenticate(username=user.username, password=password)

        if auth_user is not None:
            token, created = Token.objects.get_or_create(user=auth_user)
            return Response({
                "token": token.key,
                "user" : {
                    "id": auth_user.id,
                    "username": auth_user.username,
                    "fullname": auth_user.username,
                    "email": auth_user.email,
                }

            })
        else:
            return Response({"error": "Invalid email or password"}, status=400)





class RegistrationView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self, request):
        print("REGISTRATION REQUEST:", request.data)
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "fullname": user.username,
                    "email": user.email,
                    }
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

User = get_user_model()
class EmailCheckView(APIView):
    permission_classes = [AllowAny]

    def _find_user_by_email(self, email):
        email = (email or '').strip()
        if not email:
            return None
        return User.objects.filter(email__iexact=email).first()

    def get(self, request):
        email = request.query_params.get('email', '')
        user = self._find_user_by_email(email)
        if user:
            return Response({
                "email_exists": True,
                "id": user.id,
                "email": user.email,
                "username": getattr(user, "username", "")
            })
        return Response({"email_exists": False})

    def post(self, request):
        email = request.data.get('email', '')
        user = self._find_user_by_email(email)
        if user:
            return Response({
                "email_exists": True,
                "id": user.id,
                "email": user.email,
                "username": getattr(user, "username", "")
            })
        return Response({"email_exists": False})






class TasksReviewerView(generics.ListAPIView):
    serializer_class = TasksSerializer
    permission_classes = [isUserOrReadOnly]

    def get_queryset(self):
        return Task.objects.filter(reviewer=self.request.user)






class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TasksSerializer
    permission_classes = [IsAuthenticated]  # Vereinfacht

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Task.objects.filter(column__board__members__user=user)
        return Task.objects.none()

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        status_value = data.get("status")
        board_id = data.get("board")
        assignee_id = data.get("assignee_id")
        reviewer_id = data.get("reviewer_id")

        if assignee_id:
            try:
                User.objects.get(id=assignee_id)
            except User.DoesNotExist:
                pass

        if reviewer_id:
            try:
                User.objects.get(id=reviewer_id)
            except User.DoesNotExist:
                pass

        if status_value and board_id and not data.get("column"):
            try:
                column = Column.objects.get(
                    board_id=board_id,
                    title__iexact=status_value
                )
                data["column"] = column.id
            except Column.DoesNotExist:
                return Response(
                    {"error": f"No column found for status '{status_value}' in this board."},
                    status=400
                )

        serializer = self.get_serializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        self.perform_create(serializer)
        return Response(serializer.data, status=201)



class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            raise NotAuthenticated("You are not logged in")
        return Board.objects.filter(members__user=user)

    def perform_create(self, serializer):
        board = serializer.save(owner=self.request.user)
        default_columns = [
            ('to-do', 0),
            ('in-progress', 1),
            ('review', 2),
            ('done', 3)
        ]
        for title, position in default_columns:
            Column.objects.create(
                board=board,
                title=title,
                position=position
            )

        return board



class TasksAssignedToMeView(ListAPIView):
    serializer_class = TasksSerializer
    permission_classes = [isUserOrReadOnly]

    def get_queryset(self):
       return Task.objects.filter(assigned_to=self.request.user)


