from rest_framework import generics
from Kan_Mind_app.models import Column, Task, Comment, Board, BoardUser
from .serializers import BoardSerializer ,BoardUserSerializer, TasksSerializer, CommentSerializer, RegistrationSerializer
from rest_framework.generics import ListAPIView
from rest_framework import status, viewsets
from Kan_Mind_app.models import STATUS_CHOICES
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny ,IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import NotAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from .permissions import isOwnerOrAdmin, isUserOrReadOnly ,IsAdminForCrud, isAdminOnly, isBoardUser ,isBaordAdmin, isCommentAuthorOrAdmin

from rest_framework import generics
from Kan_Mind_app.models import Column, Task, Comment, Board, BoardUser
from .serializers import BoardSerializer, BoardUserSerializer, TasksSerializer, CommentSerializer, RegistrationSerializer
from rest_framework.generics import ListAPIView
from rest_framework import status, viewsets
from Kan_Mind_app.models import STATUS_CHOICES
from django.contrib.auth import authenticate, get_user_model

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import NotAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from .permissions import (
    isOwnerOrAdmin, isUserOrReadOnly, IsAdminForCrud,
    isAdminOnly, isBoardUser, isBaordAdmin, isCommentAuthorOrAdmin
)


# -------------------- BoardUser Views --------------------

# Handles listing all BoardUser entries and creating new ones.
# Requires authentication – only logged-in users can access.
class BoardUserView(generics.ListCreateAPIView):
    queryset = BoardUser.objects.all()
    serializer_class = BoardUserSerializer
    permission_classes = [IsAuthenticated]


# Handles retrieving, updating, or deleting a single BoardUser.
# Requires authentication.
class BoardUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BoardUser.objects.all()
    serializer_class = BoardUserSerializer
    permission_classes = [IsAuthenticated]


# -------------------- Comment Views --------------------

# Handles listing comments for a given task and creating new comments.
# Ensures the requesting user is a member of the board the task belongs to.
class CommentView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        task_id = self.kwargs.get('task_pk')
        return Comment.objects.filter(task_id=task_id).order_by('-created_at')

    def perform_create(self, serializer):
        task_id = self.kwargs.get('task_pk')
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound("Task not found.")

        user = self.request.user
        # Only allow users who are members of the board to comment
        if not BoardUser.objects.filter(board=task.column.board, user=user).exists():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You are not a member of this board.")

        serializer.save(task=task, author=user)


# Handles retrieving, updating, or deleting a single comment.
# Only the comment author can update or delete their comment.
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


# -------------------- Auth Views --------------------

# Custom login endpoint.
# Authenticates user by email + password, returns token and user info.
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
                "user": {
                    "id": auth_user.id,
                    "username": auth_user.username,
                    "fullname": auth_user.username,
                    "email": auth_user.email,
                }
            })
        return Response({"error": "Invalid email or password"}, status=400)


# Handles user registration.
# On success, returns token and created user info.
class RegistrationView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []


    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "user_id": user.id,
                "fullname": user.username,
                "email": user.email,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Checks whether an email is already registered.
# Supports both GET (query param) and POST (body).
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
                "fullname": user.username
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
                "fullname": user.username
            })
        return Response({"email_exists": False})


# -------------------- Task Views --------------------

# Returns tasks where the current user is reviewer.
class TasksReviewerView(generics.ListAPIView):
    serializer_class = TasksSerializer
    permission_classes = [isUserOrReadOnly]

    def get_queryset(self):
        return Task.objects.filter(reviewer=self.request.user)


# Main Task ViewSet.
# Provides full CRUD (list, create, retrieve, update, delete) for tasks.
# Only tasks from boards the user is a member of are visible.
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TasksSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Task.objects.filter(column__board__members__user=user)
        return Task.objects.none()

    # Custom create logic:
    # - Resolves column automatically if "status" and "board" are given.
    # - Validates assignee and reviewer existence.
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


# -------------------- Board Views --------------------

# Main Board ViewSet.
# Provides full CRUD for boards.
# Only returns boards where the user is a member.
# On creation, automatically creates default columns.
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


# -------------------- Extra Task Views --------------------

# Returns tasks where the current user is assigned.
class TasksAssignedToMeView(ListAPIView):
    serializer_class = TasksSerializer
    permission_classes = [isUserOrReadOnly]

    def get_queryset(self):
        return Task.objects.filter(assigned_to=self.request.user)
