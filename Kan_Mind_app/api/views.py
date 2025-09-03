from rest_framework import generics
from Kan_Mind_app.models import Column, Task, Comment, Board, BoardUser
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


from rest_framework import generics
from Kan_Mind_app.models import Column, Task, Comment, Board, BoardUser
from .serializers import  BoardUserSerializer, TasksSerializer, CommentSerializer, RegistrationSerializer, BoardListSerializer, BoardDetailSerializer, BoardCreateUpdateSerializer
from rest_framework.generics import ListAPIView
from rest_framework import status, viewsets
from Kan_Mind_app.models import STATUS_CHOICES
from django.contrib.auth import authenticate, get_user_model


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import NotAuthenticated ,NotFound, PermissionDenied
from rest_framework.authtoken.views import ObtainAuthToken
from .permissions import IsActiveUser





"""-------TASK VIEWS---------"""

class TasksReviewerView(generics.ListAPIView):
    """Returns tasks where the current user is reviewer."""
    serializer_class = TasksSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(reviewer=self.request.user)


class TasksAssignedToMeView(generics.ListAPIView):
    """Returns tasks where the current user is assigned."""
    serializer_class = TasksSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(assigned_to=self.request.user)


class TaskViewSet(viewsets.ModelViewSet):
    """Main Task ViewSet with full CRUD functionality."""
    queryset = Task.objects.all()
    serializer_class = TasksSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Task.objects.filter(column__board__members__user=user)
        return Task.objects.none()

    def create(self, request, *args, **kwargs):
        """Custom create logic with automatic column resolution"""
        data = request.data.copy()
        status_value = data.get("status")
        board_id = data.get("board")
        assignee_id = data.get("assignee_id")
        reviewer_id = data.get("reviewer_id")

        if assignee_id:
            try:
                assignee = User.objects.get(id=assignee_id)
                if not BoardUser.objects.filter(board_id=board_id, user=assignee).exists():
                    return Response(
                        {"error": f"User {assignee.username} is not a member of this board."},
                        status=400
                    )
            except User.DoesNotExist:
                return Response(
                    {"error": "Assignee user does not exist."},
                    status=400
                )

        if reviewer_id:
            try:
                reviewer = User.objects.get(id=reviewer_id)
                if not BoardUser.objects.filter(board_id=board_id, user=reviewer).exists():
                    return Response(
                        {"error": f"User {reviewer.username} is not a member of this board."},
                        status=400
                    )
            except User.DoesNotExist:
                return Response(
                    {"error": "Reviewer user does not exist."},
                    status=400
                )

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
        response_data = {
            "id": serializer.instance.id,
            "board": serializer.instance.column.board.id,
            "title": serializer.instance.title,
            "description": serializer.instance.description,
            "status": serializer.instance.status,
            "priority": serializer.instance.priority,
            "assignee": self._get_user_data(serializer.instance.assigned_to),
            "reviewer": self._get_user_data(serializer.instance.reviewer),
            "due_date": serializer.instance.due_date,
            "comments_count": serializer.instance.comments.count()
        }
        return Response(response_data, status=201)

    def update(self, request, *args, **kwargs):
        """Custom update logic"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        data = request.data.copy()
        status_value = data.get("status")

        if status_value and status_value != instance.status:
            try:
                column = Column.objects.get(
                    board=instance.column.board,
                    title__iexact=status_value
                )
                data["column"] = column.id
            except Column.DoesNotExist:
                return Response(
                    {"error": f"No column found for status '{status_value}' in this board."},
                    status=400
                )
        serializer = self.get_serializer(instance, data=data, partial=partial)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        self.perform_update(serializer)
        response_data = {
            "id": serializer.instance.id,
            "title": serializer.instance.title,
            "description": serializer.instance.description,
            "status": serializer.instance.status,
            "priority": serializer.instance.priority,
            "assignee": self._get_user_data(serializer.instance.assigned_to),
            "reviewer": self._get_user_data(serializer.instance.reviewer),
            "due_date": serializer.instance.due_date
        }

        return Response(response_data)

    def _get_user_data(self, user):
        """Helper method to format user data"""
        if user:
            return {
                "id": user.id,
                "email": user.email,
                "fullname": user.get_full_name() or user.username
            }
        return None






"""-------BOARD VIEWS---------"""

class BoardViewSet(viewsets.ModelViewSet):
    """Board ViewSet with Differente Serialzers"""
    queryset = Board.objects.all()
    permission_classes = [IsActiveUser]

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous or not user.is_active:
            raise NotAuthenticated("You are not logged in")
        return Board.objects.filter(members__user=user)

    def get_serializer_class(self):
        """Different Serializers for different actions"""
        if self.action == 'list':
            return BoardListSerializer
        elif self.action == 'retrieve':
            return BoardDetailSerializer
        else:
            return BoardCreateUpdateSerializer

    def perform_create(self, serializer):
        """double check, so no deleted user can create a board"""
        user = self.request.user
        if not user.is_authenticated or not user.is_active:
            raise PermissionDenied("Active authentication required")

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

    def create(self, request, *args, **kwargs):
        """Override create to return correct POST response format"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        board = self.perform_create(serializer)
        response_data = {
            "id": board.id,
            "title": board.title,
            "member_count": board.members.count(),
            "ticket_count": Task.objects.filter(column__board=board).count(),
            "tasks_to_do_count": Task.objects.filter(column__board=board, status="to-do").count(),
            "tasks_high_prio_count": Task.objects.filter(column__board=board, priority="high").count(),
            "owner_id": board.owner.id
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """Override update to return correct PATCH response format"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        board_users = BoardUser.objects.filter(board=instance)
        response_data = {
            "id": instance.id,
            "title": instance.title,
            "owner_data": {
                "id": instance.owner.id,
                "email": instance.owner.email,
                "fullname": instance.owner.get_full_name() or instance.owner.username
            },
            "members_data": [
                {
                    "id": bu.user.id,
                    "email": bu.user.email,
                    "fullname": bu.user.get_full_name() or bu.user.username
                }
                for bu in board_users
            ]
        }

        return Response(response_data, status=status.HTTP_200_OK)


class BoardUserView(generics.ListCreateAPIView):
    """ Handles listing all BoardUser entries and creating new ones.
    Requires authentication – only logged-in users can access."""
    queryset = BoardUser.objects.all()
    serializer_class = BoardUserSerializer
    permission_classes = [IsAuthenticated]

class BoardUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """ Handles retrieving, updating, or deleting a single BoardUser.
     Requires authentication."""
    queryset = BoardUser.objects.all()
    serializer_class = BoardUserSerializer
    permission_classes = [IsAuthenticated]





"""-------COMMENT VIEWS---------"""

class CommentView(generics.ListCreateAPIView):
    """ Handles listing comments for a given task and creating new comments.
     Ensures the requesting user is a member of the board the task belongs to."""
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
            raise NotFound("Task not found.")

        user = self.request.user
        """ Only allow users who are members of the board to comment"""
        if not BoardUser.objects.filter(board=task.column.board, user=user).exists():
            raise PermissionDenied("You are not a member of this board!")

        serializer.save(task=task, author=user)

class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """ Handles retrieving, updating, or deleting a single comment.
    Only the comment author can update or delete their comment."""
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        task_id = self.kwargs.get('task_pk')
        return Comment.objects.filter(task_id=task_id).select_related('author').order_by('-created_at')

    def get_object(self):
        comment = super().get_object()
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            if comment.author != self.request.user:
                raise PermissionDenied("You can only edit/delete your own comments.")
        return comment





"""-------LOGIN/REGISTRATION VIEWS---------"""

class LoginView(APIView):
    """ Custom login endpoint.
    Authenticates user by email + password, returns token and user info."""
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
                "fullname": auth_user.username,
                "email": auth_user.email,
                "user_id": auth_user.id,
            }, status=200)
        return Response({"error": "Invalid email or password"}, status=400)

class RegistrationView(APIView):
    """ Handles user registration.
     On success, returns token and created user info."""
    permission_classes = [AllowAny]
    authentication_classes = []


    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "fullname": user.username,
                "email": user.email,
                "user_id": user.id,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


User = get_user_model()
class EmailCheckView(APIView):
    """ Checks whether an email is already registered.
     Supports both GET (query param) and POST (body)."""
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










