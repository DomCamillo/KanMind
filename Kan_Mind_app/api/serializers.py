from rest_framework import serializers
from Kan_Mind_app.models import Board, BoardUser, Comment, Task, Column
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




"""-------BOARD SERIALIZER---------"""

class BoardUserSerializer(serializers.ModelSerializer):
    """Handles serialization of board members."""
    fullname = serializers.SerializerMethodField()
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = BoardUser
        fields = ['id', 'user', 'email', 'board', 'role', 'fullname']

    def get_fullname(self, obj):
        return obj.user.get_full_name() or obj.user.username



class BoardListSerializer(serializers.ModelSerializer):
    """Serializer for GET /api/boards/ """
    owner_id = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
            "id", "title", "member_count", "ticket_count",
            "tasks_to_do_count", "tasks_high_prio_count", "owner_id"
        ]

    def get_owner_id(self, obj):
        return obj.owner.id

    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return Task.objects.filter(column__board=obj).count()

    def get_tasks_to_do_count(self, obj):
        return Task.objects.filter(column__board=obj, status="to-do").count()

    def get_tasks_high_prio_count(self, obj):
        return Task.objects.filter(column__board=obj, priority="high").count()


class BoardDetailSerializer(serializers.ModelSerializer):
    """Serializer for GET /api/boards/{id}/ - with members and tasks"""
    owner_id = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ["id", "title", "owner_id", "members", "tasks"]

    def get_owner_id(self, obj):
        return obj.owner.id

    def get_members(self, obj):
        board_users = BoardUser.objects.filter(board=obj)
        return [
            {
                "id": bu.user.id,
                "email": bu.user.email,
                "fullname": bu.user.get_full_name() or bu.user.username
            }
            for bu in board_users
        ]

    def get_tasks(self, obj):
        tasks = Task.objects.filter(column__board=obj)
        return TasksSerializer(tasks, many=True).data




class BoardCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for POST/PATCH - members handling - FIXED VERSION"""
    members_input = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="List of user IDs to add as members"
    )

    owner_data = serializers.SerializerMethodField()
    members_data = serializers.SerializerMethodField()
    owner_id = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
            "id", "title", "members_input",
            "owner_id", "member_count", "ticket_count",
            "tasks_to_do_count", "tasks_high_prio_count",
            "owner_data", "members_data"
        ]

    def get_owner_id(self, obj):
        return obj.owner.id

    def get_owner_data(self, obj):
        return {
            "id": obj.owner.id,
            "email": obj.owner.email,
            "fullname": obj.owner.get_full_name() or obj.owner.username
        }

    def get_members_data(self, obj):
        board_users = BoardUser.objects.filter(board=obj)
        return [
            {
                "id": bu.user.id,
                "email": bu.user.email,
                "fullname": bu.user.get_full_name() or bu.user.username
            }
            for bu in board_users
        ]

    def get_member_count(self, obj):
        return BoardUser.objects.filter(board=obj).count()

    def get_ticket_count(self, obj):
        return Task.objects.filter(column__board=obj).count()

    def get_tasks_to_do_count(self, obj):
        return Task.objects.filter(column__board=obj, status="to-do").count()

    def get_tasks_high_prio_count(self, obj):
        return Task.objects.filter(column__board=obj, priority="high").count()

    def validate_members_input(self, value):
        """Validate that all user IDs exist and are active"""
        if not value:
            return value

        users = User.objects.filter(id__in=value, is_active=True)
        if users.count() != len(value):
            invalid_ids = set(value) - set(users.values_list('id', flat=True))
            raise serializers.ValidationError(
                f"Invalid or inactive user IDs: {list(invalid_ids)}"
            )
        return value

    def to_internal_value(self, data):
        """Maps 'members' input > 'members_input'"""
        if 'members' in data:
            data = data.copy()
            data['members_input'] = data.pop('members')
        return super().to_internal_value(data)

    def create(self, validated_data):
        """Creates board and assigns members - FIXED"""
        member_user_ids = validated_data.pop('members_input', [])
        board = Board.objects.create(**validated_data)
        BoardUser.objects.create(user=board.owner, board=board, role="owner")

        for user_id in member_user_ids:
            if user_id != board.owner.id:
                try:
                    user = User.objects.get(id=user_id, is_active=True)
                    BoardUser.objects.create(user=user, board=board, role="member")
                except User.DoesNotExist:
                    continue

        return board

    def update(self, instance, validated_data):
        """Updates board and replaces members - FIXED"""
        member_user_ids = validated_data.pop('members_input', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if member_user_ids is not None:
            BoardUser.objects.filter(board=instance, role="member").delete()

            for user_id in member_user_ids:
                if user_id != instance.owner.id:
                    try:
                        user = User.objects.get(id=user_id, is_active=True)
                        BoardUser.objects.get_or_create(
                            user=user,
                            board=instance,
                            defaults={'role': 'member'}
                        )
                    except User.DoesNotExist:
                        continue
        return instance







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





"""-------REGISTRATION SERIALIZER---------"""

class RegistrationSerializer(serializers.ModelSerializer):
    """ Handles user registration.
     Includes password confirmation and maps fullname → username"""
    repeated_password = serializers.CharField(write_only=True)
    fullname = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['fullname', 'email', 'password', 'repeated_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    """  Ensure email is unique"""
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists')
        return value

    """ Ensure both passwords match"""
    def validate(self, data):
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError(
                {'password': 'Passwords do not match'})
        return data
    def create(self, validated_data):
        validated_data['username'] = validated_data.pop('fullname')
        validated_data.pop('repeated_password')
        user = User(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
