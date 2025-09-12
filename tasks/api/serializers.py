from rest_framework import serializers
from tasks.models import Comment, Task
from boards.models import Column ,Board, BoardUser
from django.contrib.auth import get_user_model
User = get_user_model()

"""-------TASK SERIALIZER---------"""

class TasksSerializer(serializers.ModelSerializer):
    """Handles all logic related to Task serialization """
    assignee = serializers.SerializerMethodField()
    reviewer = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    board = serializers.SerializerMethodField()

    column = serializers.PrimaryKeyRelatedField(
        queryset=Column.objects.all(),
        write_only=True,
        required=False
    )

    assignee_id = serializers.IntegerField(
        write_only=True,
        required=False,
        allow_null=True
    )

    reviewer_id = serializers.IntegerField(
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Task
        fields = [
            "id", "board", "title", "description", "status", "priority",
            "assignee", "reviewer", "assignee_id", "reviewer_id",
            "due_date", "comments_count", "column"
        ]

    def get_board(self, obj):
        return obj.column.board.id

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_assignee(self, obj):
        if obj.assigned_to:
            return {
                "id": obj.assigned_to.id,
                "email": obj.assigned_to.email,
                "fullname": obj.assigned_to.get_full_name() or obj.assigned_to.username
            }
        return None

    def get_reviewer(self, obj):
        if obj.reviewer:
            return {
                "id": obj.reviewer.id,
                "email": obj.reviewer.email,
                "fullname": obj.reviewer.get_full_name() or obj.reviewer.username
            }
        return None

    def validate_assignee_id(self, value):
        """Validate assignee_id field"""
        if value is None:
            return None
        if not isinstance(value, int):
            try:
                value = int(value)
            except (ValueError, TypeError):
                raise serializers.ValidationError("assignee_id must be a valid integer.")
        try:
            user = User.objects.get(id=value, is_active=True)
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError(f"User with ID {value} does not exist or is inactive.")

    def validate_reviewer_id(self, value):
        """Validate reviewer_id field"""
        if value is None:
            return None
        if not isinstance(value, int):
            try:
                value = int(value)
            except (ValueError, TypeError):
                raise serializers.ValidationError("reviewer_id must be a valid integer.")
        try:
            user = User.objects.get(id=value, is_active=True)
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError(f"User with ID {value} does not exist or is inactive.")

    def validate(self, data):
        """Validation to ensure assignee and reviewer belong to the board"""
        board = None
        column = data.get('column')
        if column:
            board = column.board
        elif hasattr(self, 'instance') and self.instance and self.instance.column:
            board = self.instance.column.board
        elif hasattr(self, 'context') and 'board' in self.context:
            board = self.context['board']

        if not board:
            return data
        assigned_to = data.get('assignee_id')
        if assigned_to:
            if not BoardUser.objects.filter(board=board, user=assigned_to).exists():
                raise serializers.ValidationError({
                    'assignee_id': f'User {assigned_to.username} is not a member of this board.'
                })
            data['assigned_to'] = assigned_to

        reviewer = data.get('reviewer_id')
        if reviewer:
            if not BoardUser.objects.filter(board=board, user=reviewer).exists():
                raise serializers.ValidationError({
                    'reviewer_id': f'User {reviewer.username} is not a member of this board.'
                })
            data['reviewer'] = reviewer
        data.pop('assignee_id', None)
        data.pop('reviewer_id', None)

        return data




"""-------COMMENT SERIALIZER---------"""

class CommentSerializer(serializers.ModelSerializer):
    """ Handles serialization of comments.
     Includes author details and task reference."""
    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'author', 'content', 'created_at']

    def get_author(self, obj):
        return obj.author.get_full_name() or obj.author.username