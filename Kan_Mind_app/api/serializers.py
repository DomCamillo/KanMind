from rest_framework import serializers
from Kan_Mind_app.models import Board, BoardUser, Comment, Task
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
User = get_user_model()




"""-------TASK SERIALIZER---------"""

class TasksSerializer(serializers.ModelSerializer):
    """Handles all logic related to Task serialization."""
    assignee = serializers.SerializerMethodField()
    reviewer = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    board = serializers.SerializerMethodField()

    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="assigned_to",
        write_only=True,
        required=False,
        allow_null=True
    )

    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="reviewer",
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Task
        fields = [
            "id", "board", "title", "description", "status", "priority",
            "assignee", "reviewer", "assignee_id", "reviewer_id",
            "due_date", "comments_count"
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

    def validate(self, data):
        """Validation to ensure assignee and reviewer belong to the board"""
        column = data.get('column')
        board = None

        if column:
            board = column.board
        elif hasattr(self, 'instance') and self.instance:
            board = self.instance.column.board

        assigned_to = data.get('assigned_to')
        reviewer = data.get('reviewer')

        if board and assigned_to:
            if not BoardUser.objects.filter(board=board, user=assigned_to).exists():
                raise serializers.ValidationError({
                    'assignee_id': f'User {assigned_to.username} is not a member of this board.'
                })

        if board and reviewer:
            if not BoardUser.objects.filter(board=board, user=reviewer).exists():
                raise serializers.ValidationError({
                    'reviewer_id': f'User {reviewer.username} is not a member of this board.'
                })
        return data

    def create(self, validated_data):
        """Custom create logic for tasks"""
        return Task.objects.create(**validated_data)






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
    """Serializer for POST/PATCH - members handling"""
    members_input = serializers.PrimaryKeyRelatedField(
        source='members',
        many=True,
        queryset=User.objects.all(),
        write_only=True,
        required=False
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
        return obj.members.count()

    def get_ticket_count(self, obj):
        return Task.objects.filter(column__board=obj).count()

    def get_tasks_to_do_count(self, obj):
        return Task.objects.filter(column__board=obj, status="to-do").count()

    def get_tasks_high_prio_count(self, obj):
        return Task.objects.filter(column__board=obj, priority="high").count()

    def to_internal_value(self, data):
        """Maps 'members' input > 'members_input'
        makes a dict from the raw input data"""
        if 'members' in data:
            data = data.copy()
            data['members_input'] = data.pop('members')
        return super().to_internal_value(data)

    def create(self, validated_data):
        """Creates board and assigns members"""
        member_users = validated_data.pop('members', [])
        board = Board.objects.create(**validated_data)

        BoardUser.objects.create(user=board.owner, board=board, role="owner")

        for user in member_users:
            if user != board.owner:
                BoardUser.objects.create(user=user, board=board, role="member")

        return board

    def update(self, instance, validated_data):
        """Updates board and replaces members"""
        member_users = validated_data.pop('members', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()


        if member_users is not None:
            BoardUser.objects.filter(board=instance).exclude(role="owner").delete()

            for user in member_users:
                if user != instance.owner:
                    BoardUser.objects.get_or_create(user=user, board=instance, defaults={'role': 'member'})
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
