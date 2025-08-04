from rest_framework import serializers
from Kan_Mind_app.models import Board ,BoardUser, Column , Comment, Task
from django.contrib.auth.models import User



class BoardSerializer(serializers.ModelSerializer):
    members = serializers.ListField(child=serializers.EmailField(), write_only=True, required=False)
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Board
        fields = ['id', 'title', 'created_at', 'owner', 'members']
        read_only_fields = ['id', 'created_at', 'owner']

    def create(self, validated_data):
        members_emails = validated_data.pop('members', [])
        board = Board.objects.create(**validated_data)
        BoardUser.objects.create(user=board.owner, board=board, role="owner")

        for email in members_emails:
            try:
                user = User.objects.get(email=email)
                BoardUser.objects.create(user=user, board=board, role="member")
            except User.DoesNotExist:
                raise serializers.ValidationError({"email": f"User with email {email} does not exist."})

        return board


# class UserSerializer(serializers.ModelSerializer):
#     fullname = serializers.SerializerMethodField()
#     class Meta:
#         model = User
#         fields = ['id', 'email', 'fullname']

#     def get_fullname(self, obj):
#         return obj.get_full_name() or obj.username


class BoardUserSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()
  #  user = UserSerializer(read_only=True)
    class Meta:
        model = BoardUser
        fields = ['id', 'user','board', 'role', 'fullname']

    def get_fullname(self, obj):
        return obj.user.get_full_name() or obj.user.username


class ColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Column
        fields = ['board', 'title', 'position']


class TasksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields ='__all__'


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['task', 'author', 'content', 'created_at']



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
            raise serializers.ValidationError({'password': 'Passwords do not match'})
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















## DA Project
# class RegistrationSerializer(serializers.ModelSerializer):

#     repeated_password = serializers.CharField(write_only=True)

#     class Meta:
#         model = User # ein serializer fuer das user model
#         fields = ['username', 'email', 'password', 'repeated_password']
#         extra_kwargs = {
#             'password':{
#                 'write_only': True
#             }
#         }

#     def validate_email(self, value):
#         if User.objects.filter(email=value).exists():
#             raise serializers.ValidationError('Email already exists')
#         return value

#     def save(self):
#         email = self.validated_data['email']
#         pw = self.validated_data['password']
#         repeated_pw = self.validated_data['repeated_password']
#         username = self.validated_data['username']

#         if pw != repeated_pw:
#             raise serializers.ValidationError({'error': 'passwords dont match'})

#         account = User(email=email, username=username)
#         account.set_password(pw)
#         account.save()
#         return account
