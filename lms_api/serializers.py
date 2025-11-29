from rest_framework import serializers
from django.contrib.auth.models import User  # <-- IMPORTANTE
from .models import Profile, Course, Lesson, Enrollment, Comment

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "is_active", "date_joined"]
        read_only_fields = ["id", "date_joined"]


class ProfileSerializer(serializers.ModelSerializer):
    bio = serializers.CharField(max_length=200, allow_blank=True, required=False)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    user_info = UserSerializer(source="user", read_only=True)

    class Meta:
        model = Profile
        fields = ["id", "user", "user_info", "name", "role", "bio", "avatar", "created_at", "updated_at"]
        read_only_fields = ["id", "user", "created_at"]


class CourseSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    owner_info = UserSerializer(source="owner", read_only=True)

    class Meta:
        model = Course
        fields = [
            "id","owner","owner_info","title","subtitle","description","level","language","category",
            "what_you_will_learn","requirements","target_audience","price","duration_hours","created_at",
        ]
        read_only_fields = ["id","owner","created_at"]


class LessonSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())

    class Meta:
        model = Lesson
        fields = ["id", "course", "title", "content", "video_url", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class EnrollmentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    user_info = UserSerializer(source="user", read_only=True)
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    status = serializers.ChoiceField(choices=["active", "completed", "canceled"], default="active")

    class Meta:
        model = Enrollment
        fields = [
            "id","user","user_info","course","status","progress","enrolled_at","updated_at",
        ]
        read_only_fields = ["id","user","enrolled_at","updated_at"]


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    user_info = UserSerializer(source="user", read_only=True) 
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())

    class Meta:
        model = Comment
        fields = ["id", "course", "user", "user_info", "body", "rating", "created_at", "updated_at"]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

    def validate_rating(self, value):
        if value is None:
            return value
        if not (1 <= value <= 5):
            raise serializers.ValidationError("rating debe estar entre 1 y 5.")
        return value
