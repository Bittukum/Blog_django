from rest_framework import serializers
from .models import (CustomUser,BlogPost,Comment,Like)

class UserSignupSerializer(serializers.ModelSerializer):
    """ Serializer for Sign up the new user"""

    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'gender', 'password']

    def create(self, validated_data):
        user = CustomUser(
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            gender=validated_data.get('gender', ''),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id','email', 'first_name', 'last_name', 'gender']

class BlogPostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)  # Use the UserSerializer for author

    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'content', 'author', 'created_at', 'updated_at']
        read_only_fields = ['author', 'created_at', 'updated_at']

    def validate(self, data):
        # Custom validation logic
        if not data.get('title'):
            raise serializers.ValidationError({'title': 'Title is required.'})
        if not data.get('content'):
            raise serializers.ValidationError({'content': 'Content is required.'})
        return data

    def create(self, validated_data):
        # Automatically assign the current user as the author
        user = self.context['request'].user
        return BlogPost.objects.create (**validated_data)

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'blog_post', 'author', 'content', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'comment', 'user', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    subject = serializers.CharField(max_length=255)
    message = serializers.CharField()