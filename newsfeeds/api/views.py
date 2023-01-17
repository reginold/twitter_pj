from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from newsfeeds.api.serializers import NewsFeedSerializer
from newsfeeds.models import NewsFeed


class NewsFeedViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return NewsFeed.objects.filter(user=self.request.user)

    def list(self, request):
        serializer = NewsFeedSerializer(
            self.get_queryset(), context={"request": request}, many=True
        )
        return Response(
            {
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
