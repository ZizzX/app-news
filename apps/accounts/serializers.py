from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'password_confirm')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user
    

class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(request=self.context.get('request'), username=email, password=password)
            if not user:
                raise serializers.ValidationError({"detail": "Invalid credentials."})
            if  not user.is_active:
                raise serializers.ValidationError({"detail": "User account is disabled."})
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError({"detail": "Must include 'email' and 'password'."})
        

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile.
    """
    full_name = serializers.ReadOnlyField()
    posts_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'avatar', 'bio', 'created_at', 'updated_at', 'posts_count', 'comments_count')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_posts_count(self, obj):
        # Return 0 if related manager 'posts' doesn't exist
        related = getattr(obj, 'posts', None)
        try:
            return related.count() if related is not None else 0
        except Exception:
            return 0

    def get_comments_count(self, obj):
        # Return 0 if related manager 'comments' doesn't exist
        related = getattr(obj, 'comments', None)
        try:
            return related.count() if related is not None else 0
        except Exception:
            return 0
    

class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile.
    """
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'avatar', 'bio')
    
    def validate_avatar(self, value):
        if value.size > 2 * 1024 * 1024:  # 2MB limit
            raise serializers.ValidationError("Avatar size should not exceed 2MB.")
        return value
    
    def update(self, instance, validated_data):
        for  attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
    
class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing user password.
    """
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "New password fields didn't match."})
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct.")
        return value
    
    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user