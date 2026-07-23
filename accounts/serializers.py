from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator
from rest_framework import serializers

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True,
        validators=[MinLengthValidator(8)],
    )
    email = serializers.EmailField(required=True)
    username = serializers.CharField(
        required=True,
        validators=[MinLengthValidator(2)],
    )
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    