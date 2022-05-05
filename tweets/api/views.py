from newsfeeds.services import NewsFeedServices
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from tweets.api.serializers import (
    TweetSerializer,
    TweetSerializerForCreate,
    TweetSerializerWithComments,
)
from tweets.models import Tweet
from utils.decorators import required_params


class TweetViewSet(viewsets.GenericViewSet):
    queryset = Tweet.objects.all()
    serializer_class = TweetSerializerForCreate

    # POST /api/tweets/ -> create
    # GET /api/tweets/?tweets_id=1 -> list
    # GET /api/tweets/1/1 -> retrieve
    def get_permissions(self):
        # self.action --> (list, create) func
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    def retrieve(self, request, *args, **kwargs):
        tweet = self.get_object()
        return Response(TweetSerializerWithComments(tweet).data)

    @required_params(params=["user_id"])
    def list(self, request, *args, **kwargs):
        user_id = request.query_params["user_id"]
        tweets = Tweet.objects.filter(user_id=user_id).order_by("-created_at")

        # set the many=True, return list of dict
        serializer = TweetSerializer(tweets, many=True)
        return Response({"tweets": serializer.data})

    def create(self, request):
        serializer = TweetSerializerForCreate(
            data=request.data,
            context={"request": request},
        )

        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Please check the input",
                    "errors": serializer.errors,
                },
                status=400,
            )

        # save the serializer would call create method in TweetSerializerForCreate
        tweet = serializer.save()
        NewsFeedServices.fanout_to_followers(tweet)
        return Response(TweetSerializer(tweet).data, status=201)
