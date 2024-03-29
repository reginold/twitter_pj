from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from inbox.services import NotificationService
from likes.api.serializers import (
    LikeSerializer,
    LikeSerializerForCancel,
    LikeSerializerForCreate,
)
from likes.models import Like
from utils.decorators import required_params


class LikeViewSet(viewsets.GenericViewSet):
    queryset = Like.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = LikeSerializerForCreate

    @required_params(method="POST", params=["content_type", "object_id"])
    def create(self, request, *args, **kwargs):
        serializer = LikeSerializerForCreate(
            data=request.data,
            context={"request": request},
        )

        if not serializer.is_valid():
            return Response(
                {
                    "message": "Please check input",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance, created = serializer.get_or_create()
        if created:
            NotificationService.send_like_notification(instance)
        return Response(
            LikeSerializer(instance).data,
            status=status.HTTP_201_CREATED,
        )

    @action(methods=["POST"], detail=False)
    @required_params(method="POST", params=["content_type", "object_id"])
    def cancel(self, request, *args, **kwargs):
        serailizer = LikeSerializerForCancel(
            data=request.data,
            context={"request": request},
        )

        if not serailizer.is_valid():
            return Response(
                {
                    "message": "Please check input",
                    "errors": serailizer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        deleted = serailizer.cancel()
        return Response(
            {
                "success": True,
                "deleted": deleted,
            },
            status=status.HTTP_200_OK,
        )
