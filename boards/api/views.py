
from tasks.models import Comment, Task
from boards.models import Column ,Board, BoardUser
from authentication.api.permissions import IsActiveUser
from .serializers import  BoardUserSerializer, TasksSerializer,  BoardListSerializer, BoardDetailSerializer, BoardCreateUpdateSerializer
from django.contrib.auth import authenticate, get_user_model

from django.http import Http404
from rest_framework import generics
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import NotAuthenticated ,NotFound, PermissionDenied ,ValidationError




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
