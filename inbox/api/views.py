from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from inbox.api.serializers import (
    NotificationSerializer,
    NotificationSerializerForUpdate,
)
from utils.decorators import required_params


class NotificationViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.ListModelMixin,
):
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)
    filterset_fields = ("unread",)

    def get_queryset(self):
        return self.request.user.notifications.all()

    # GET /api/notifications/unread-count/
    @action(methods=["GET"], detail=False, url_path="unread-count")
    def unread_count(self, request, *args, **kwargs):
        count = self.get_queryset().filter(unread=True).count()
        return Response({"unread_count": count}, status=status.HTTP_200_OK)

    # POST /api/notifications/mark-all-as-read/
    @action(methods=["POST"], detail=False, url_path="mark-all-as-read")
    def mark_all_as_read(self, request, *args, **kwargs):
        updated_count = self.get_queryset().update(unread=False)
        return Response({"marked_count": updated_count}, status=status.HTTP_200_OK)

    @required_params(method="POST", params=["unread"])
    def update(self, request, *args, **kwargs):
        serializer = NotificationSerializerForUpdate(
            instance=self.get_object(),
            data=request.data,
        )
        if not serializer.is_valid():
            return Response(
                {
                    "message": "Please check the input",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        notification = serializer.save()
        return Response(
            NotificationSerializer(notification).data, status=status.HTTP_200_OK
        )
