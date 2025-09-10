from Kan_Mind_app.models import Column, Task, Comment, Board, BoardUser ,STATUS_CHOICES
from .permissions import IsActiveUser
from .serializers import  BoardUserSerializer, TasksSerializer, CommentSerializer, RegistrationSerializer, BoardListSerializer, BoardDetailSerializer, BoardCreateUpdateSerializer
from django.contrib.auth import authenticate, get_user_model

from django.http import Http404
from rest_framework import generics
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import NotAuthenticated ,NotFound, PermissionDenied ,ValidationError
from rest_framework import serializers






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

    def get_object(self):
        """Override to return 403 instead of 404 for permission issues"""
        try:
            obj = Task.objects.get(pk=self.kwargs['pk'])
            if not BoardUser.objects.filter(board=obj.column.board, user=self.request.user).exists():
                raise PermissionDenied("You don't have access to tasks in this board.")
            return obj
        except Task.DoesNotExist:
            raise Http404("Task not found.")

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Task.objects.filter(column__board__members__user=user)
        return Task.objects.none()

    def _get_status_key_from_display(self, status_input):
        """Convert User-Input to correct Status-Key"""
        if not status_input:
            return None

        status_choices = dict(STATUS_CHOICES)
        if status_input in status_choices:
            return status_input

        for key, display_name in status_choices.items():
            if display_name.lower() == status_input.lower():
                return key
        return None

    def _handle_status_column_mapping(self, data, board):
        """Maps status to column and validates"""
        status_value = data.get("status")
        if not status_value or data.get("column"):
            return

        valid_status_key = self._get_status_key_from_display(status_value)
        if not valid_status_key:
            raise serializers.ValidationError({
                "status": f"Invalid status '{status_value}'. Valid options: {[key for key, _ in STATUS_CHOICES]}"
            })

        data["status"] = valid_status_key

        try:
            column = Column.objects.get(title=valid_status_key, board=board)
            data["column"] = column.id
        except Column.DoesNotExist:
            raise serializers.ValidationError({
                "status": f"No column found for status '{valid_status_key}' in this board."
            })

    def create(self, request, *args, **kwargs):
        """Custom create logic with board validation"""
        data = request.data.copy()
        board_id = data.get("board")
        if not board_id:
            return Response(
                {"error": "Board ID is required."},
                status=status.HTTP_400_BAD_REQUEST)

        try:
            board = Board.objects.get(id=board_id)
            if not BoardUser.objects.filter(board=board, user=request.user).exists():
                return Response(
                    {"error": "You don't have access to this board."},
                    status=status.HTTP_403_FORBIDDEN)
        except Board.DoesNotExist:
            return Response(
                {"error": "Board not found."},
                status=status.HTTP_404_NOT_FOUND)
        try:
            self._handle_status_column_mapping(data, board)
        except serializers.ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=data, context={'board': board})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        return Response(self._get_task_response_data(serializer.instance), status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """Custom update logic"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()

        if data.get("status") and data["status"] != instance.status:
            try:
                self._handle_status_column_mapping(data, instance.column.board)
            except serializers.ValidationError as e:
                return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(
            instance,
            data=data,
            partial=partial,
            context={'board': instance.column.board}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        self.perform_update(serializer)
        return Response(self._get_task_response_data(serializer.instance, include_comments_count=False))

    def _get_task_response_data(self, task_instance, include_comments_count=True):
        """Helper for consistent Response-Data"""
        data = {
            "id": task_instance.id,
            "title": task_instance.title,
            "description": task_instance.description,
            "status": task_instance.status,
            "priority": task_instance.priority,
            "assignee": self._get_user_data(task_instance.assigned_to),
            "reviewer": self._get_user_data(task_instance.reviewer),
            "due_date": task_instance.due_date
        }

        if include_comments_count:
            data.update({
                "board": task_instance.column.board.id,
                "comments_count": task_instance.comments.count()
            })
        return data

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

    def get_object(self):
        """Return 403 instead of 404 for permission issues"""
        try:
            obj = Board.objects.get(pk=self.kwargs['pk'])
            if not BoardUser.objects.filter(board=obj, user=self.request.user).exists():
                raise PermissionDenied("You don't have access to this board.")
            return obj
        except Board.DoesNotExist:
            raise Http404("Board not found.")

    def get_serializer_class(self):
        """Different Serializers for different actions"""
        if self.action == 'list':
            return BoardListSerializer
        elif self.action == 'retrieve':
            return BoardDetailSerializer
        else:
            return BoardCreateUpdateSerializer

    def perform_create(self, serializer):
        """Double check, so no deleted user can create a board"""
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
    """Handles listing and creating comments for a task."""
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def _get_task_and_validate_access(self):
        """Helper to get task and validate user access"""
        task_id = self.kwargs.get('task_pk')

        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return None, Response(
                {"error": "Task not found."},
                status=status.HTTP_404_NOT_FOUND)

        if not BoardUser.objects.filter(board=task.column.board, user=self.request.user).exists():
            return None, Response(
                {"error": "You are not a member of this board."},
                status=status.HTTP_403_FORBIDDEN)
        return task, None

    def get_queryset(self):
        task, error_response = self._get_task_and_validate_access()
        if error_response:
            return Comment.objects.none()
        return Comment.objects.filter(task=task).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        task, error_response = self._get_task_and_validate_access()
        if error_response:
            return error_response
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        task, error_response = self._get_task_and_validate_access()
        if error_response:
            return error_response

        if not request.data.get('content', '').strip():
            return Response(
                {"error": "Content is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(task=task, author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Handles retrieving, updating, or deleting a single comment."""
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        task_id = self.kwargs.get('task_pk')
        return Comment.objects.filter(task_id=task_id).select_related('author')

    def get_object(self):
        task_id = self.kwargs.get('task_pk')
        comment_id = self.kwargs.get('pk')
        try:
            task = Task.objects.get(id=task_id)
            if not BoardUser.objects.filter(board=task.column.board, user=self.request.user).exists():
                raise PermissionDenied("You are not a member of this board.")
        except Task.DoesNotExist:
            raise NotFound("Task not found.")
        try:
            comment = Comment.objects.get(id=comment_id, task_id=task_id)
            if self.request.method in ['PUT', 'PATCH', 'DELETE'] and comment.author != self.request.user:
                raise PermissionDenied("You can only edit/delete your own comments.")
            return comment
        except Comment.DoesNotExist:
            raise NotFound("Comment not found.")





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










