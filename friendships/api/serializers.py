from accounts.api.serializers import UserSerializerForFriendship
from django.contrib.auth.models import User
from friendships.models import Friendship
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class FollowerSerializer(serializers.ModelSerializer):
    user = UserSerializerForFriendship(source="from_user")

    class Meta:
        model = Friendship
        fields = ["user", "created_at"]


class FollowingSerializer(serializers.ModelSerializer):
    user = UserSerializerForFriendship(source="to_user")
    created_at = serializers.DateTimeField()

    class Meta:
        model = Friendship
        fields = ["user", "created_at"]


class FriendshipSerializerForCreate(serializers.ModelSerializer):
    from_user_id = serializers.IntegerField()
    to_user_id = serializers.IntegerField()

    class Meta:
        model = Friendship
        fields = ["from_user_id", "to_user_id"]

    def validate(self, attrs):
        if attrs["from_user_id"] == attrs["to_user_id"]:
            raise ValidationError(
                {"message": "from_user_id and to_user_id should be different"}
            )

        if not User.objects.filter(id=attrs["to_user_id"]).exists():
            raise ValidationError({"message": "You cannot follow a non-exist user."})
        return attrs

    def create(self, validated_data):
        from_user_id = validated_data["from_user_id"]
        to_user_id = validated_data["to_user_id"]
        return Friendship.objects.create(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
        )
