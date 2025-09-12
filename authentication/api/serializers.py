from rest_framework import serializers

from django.contrib.auth import get_user_model
User = get_user_model()



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
