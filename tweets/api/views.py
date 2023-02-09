from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from newsfeeds.services import NewsFeedServices
from tweets.api.serializers import (
    TweetSerializer,
    TweetSerializerForCreate,
    TweetSerializerForDetail,
)
from tweets.models import Tweet
from tweets.services import TweetService
from utils.decorators import required_params
from utils.paginations import EndlessPagination


class TweetViewSet(viewsets.GenericViewSet):
    queryset = Tweet.objects.all()
    serializer_class = TweetSerializerForCreate
    pagination_class = EndlessPagination

    # POST /api/tweets/ -> create
    # GET /api/tweets/?tweets_id=1 -> list
    # GET /api/tweets/1/1 -> retrieve
    def get_permissions(self):
        # self.action --> (list, create) func
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    def retrieve(self, request, *args, **kwargs):
        serializer = TweetSerializerForDetail(
            self.get_object(),
            context={"request": request},
        )
        return Response(serializer.data)

    @required_params(params=["user_id"])
    def list(self, request, *args, **kwargs):
        user_id = request.query_params["user_id"]
        tweets = TweetService.get_cached_tweets(user_id=user_id)
        tweets = self.paginate_queryset(tweets)

        # set the many=True, return list of dict
        serializer = TweetSerializer(tweets, context={"request": request}, many=True)
        return self.get_paginated_response(serializer.data)

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
        serializer = TweetSerializer(tweet, context={"request": request})
        return Response(serializer.data, status=201)
