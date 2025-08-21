from rest_framework import serializers
from Kan_Mind_app.models import Board, BoardUser, Column, Comment, Task
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
User = get_user_model()


class TasksSerializer(serializers.ModelSerializer):
    assignee = serializers.SerializerMethodField()
    reviewer = serializers.SerializerMethodField()

    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=BoardUser.objects.all(),
        source="assigned_to",
        write_only=True,
        required=False,
        allow_null=True
    )

    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=BoardUser.objects.all(),
        source="reviewer",
        write_only=True,
        required=False,
        allow_null=True
    )

    board = serializers.PrimaryKeyRelatedField(
        queryset=Board.objects.all(),
        write_only=True,
        required=False
    )
    column_title = serializers.CharField(source="column.title", read_only=True)

    class Meta:
        model = Task
        fields = [
            "id", "title", "description", "status", "priority", "due_date",
            "column", "column_title", "board", "assignee", "reviewer",
            "assignee_id", "reviewer_id", "created_at", "updated_at"
        ]

    def get_assignee(self, obj):
        if obj.assigned_to:
            return {
                "id": obj.assigned_to.id,
                "fullname": obj.assigned_to.get_full_name() or obj.assigned_to.username,
                "username": obj.assigned_to.username,
                "email": obj.assigned_to.email
            }
        return None

    def get_reviewer(self, obj):
        if obj.reviewer:
            return {
                "id": obj.reviewer.id,
                "fullname": obj.reviewer.get_full_name() or obj.reviewer.username,
                "username": obj.reviewer.username,
                "email": obj.reviewer.email
            }
        return None

    def validate(self, data):
        board = data.get('board')
        assigned_to = data.get('assigned_to')
        reviewer = data.get('reviewer')

        if board and isinstance(assigned_to, BoardUser):
            if not BoardUser.objects.filter(board=board, user=assigned_to.user).exists():
                raise serializers.ValidationError({
                    'assignee_id': f'User {assigned_to.user.username} is not a member of this board.'
                })

        if board and isinstance(reviewer, BoardUser):
            if not BoardUser.objects.filter(board=board, user=reviewer.user).exists():
                raise serializers.ValidationError({
                    'reviewer_id': f'User {reviewer.user.username} is not a member of this board.'
                })
        return data

    def create(self, validated_data):
        board = validated_data.pop("board", None)
        assigned_to = validated_data.pop("assigned_to", None)
        reviewer = validated_data.pop("reviewer", None)

        # Column anhand des Boards bestimmen (z.B. default: erste Column im Board)
        if board and "column" not in validated_data:
            first_column = board.column_set.first()
            if not first_column:
                raise serializers.ValidationError("Board has no columns.")
            validated_data["column"] = first_column

        if isinstance(assigned_to, BoardUser):
            validated_data["assigned_to"] = assigned_to.user
        if isinstance(reviewer, BoardUser):
            validated_data["reviewer"] = reviewer.user

        return Task.objects.create(**validated_data)



class BoardUserSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = BoardUser
        fields = ['id', 'user', 'email', 'board', 'role', 'fullname']

    def get_fullname(self, obj):
        return obj.user.get_full_name() or obj.user.username



class BoardSerializer(serializers.ModelSerializer):
    members = BoardUserSerializer(many=True, read_only=True)
    members_input = serializers.PrimaryKeyRelatedField(
        source='members',
        many=True,
        queryset=User.objects.all(),
        write_only=True,
        required=False
    )

    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
            "id", "title", "created_at", "owner",
            "members", "members_input",
            "member_count", "ticket_count",
            "tasks_to_do_count", "tasks_high_prio_count", "tasks",
        ]

    def get_members(self, obj):
        board_users = BoardUser.objects.filter(board=obj)
        return BoardUserSerializer(board_users, many=True).data

    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return Task.objects.filter(column__board=obj).count()

    def get_tasks_to_do_count(self, obj):
        return Task.objects.filter(column__board=obj, status="to-do").count()

    def get_tasks_high_prio_count(self, obj):
        return Task.objects.filter(column__board=obj, priority="high").count()

    def get_tasks(self, obj):
        tasks = Task.objects.filter(column__board=obj)
        return TasksSerializer(tasks, many=True).data

    def to_internal_value(self, data):
        if 'members' in data:
            data = data.copy()
            data['members_input'] = data.pop('members')
        return super().to_internal_value(data)

    def create(self, validated_data):
        member_users = validated_data.pop('members', [])
        board = Board.objects.create(**validated_data)

        BoardUser.objects.create(user=board.owner, board=board, role="owner")

        for user in member_users:
            if user != board.owner:
                BoardUser.objects.create(user=user, board=board, role="member")

        return board



class ColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Column
        fields = ['id', 'board', 'title', 'position']


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    task = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'task', 'author', 'content', 'created_at']

    def get_author(self, obj):

        return obj.author.get_full_name() or obj.author.username


class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)
    fullname = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['fullname', 'email', 'password', 'repeated_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists')
        return value

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
