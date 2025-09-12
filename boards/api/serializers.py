from rest_framework import serializers
from tasks.models import Comment, Task
from boards.models import Column ,Board, BoardUser
from tasks.api.serializers import TasksSerializer
from django.contrib.auth import get_user_model
User = get_user_model()




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


