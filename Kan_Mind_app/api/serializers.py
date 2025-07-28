from rest_framework import serializers
from kan_mind_app.models import Board ,BoardUser, Column , Comment, Task
from django.contrib.auth.models import User



class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ['title', 'created_at', 'owner']



class BoardUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardUser
        fields = ['user','board', 'role']


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

    class Meta:
        model = User # ein serializer fuer das user model
        fields = ['username', 'email', 'password', 'repeated_password']
        extra_kwargs = {
            'password':{
                'write_only': True
            }
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists')
        return value

    def save(self):
        email = self.validated_data['email']
        pw = self.validated_data['password']
        repeated_pw = self.validated_data['repeated_password']
        username = self.validated_data['username']

        if pw != repeated_pw:
            raise serializers.ValidationError({'error': 'passwords dont match'})

        account = User(email=email, username=username)
        account.set_password(pw)
        account.save()
        return account
