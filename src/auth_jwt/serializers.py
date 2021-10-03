from rest_framework import serializers
from django.contrib.auth import get_user_model

# Returns default Django User model from models.User
UserModel = get_user_model()


class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, data):
        user = UserModel.objects.create_user(
            username=data['username'],
            password=data['password'],
        )
        return user

    class Meta:
        model = UserModel
        fields = ('username', 'first_name', 'last_name', 'password', )


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ('first_name', 'last_name')
