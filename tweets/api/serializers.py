from accounts.api.serializers import UserSerializer
from rest_framework import serializers
from tweets.models import Tweet


class TweetSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Tweet
        fields = "__all__"


class TweetSerializerForCreate(serializers.ModelSerializer):

    content = serializers.CharField(min_length=6, max_length=140)

    class Meta:
        model = Tweet
        fields = "__all__"

    def create(self, validated_data):
        user = self.context["request"].user
        content = validated_data["content"]
        tweet = Tweet.objects.create(user=user, content=content)
        return tweet
