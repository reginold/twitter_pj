from comments.api.serializers import (
    CommentSerializer,
    CommentSerializerForCreate,
    CommentSerializerForUpdate,
)
from comments.models import Comment
from inbox.services import NotificationService
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from utils.decorators import required_params
from utils.permissions import IsObjectOwner


class CommentViewSet(viewsets.GenericViewSet):
    """
    只实现 list, create, update, destroy 的方法
    不实现 retrieve（查询单个 comment） 的方法，因为没这个需求
    """

    serializer_class = CommentSerializerForCreate
    queryset = Comment.objects.all()
    filterset_fields = ("tweet_id",)

    def get_permissions(self):
        # 注意要加用 AllowAny() / IsAuthenticated() 实例化出对象
        # 而不是 AllowAny / IsAuthenticated 这样只是一个类名
        if self.action == "create":
            return [IsAuthenticated()]
        if self.action in ["destroy", "update"]:
            return [IsAuthenticated(), IsObjectOwner()]
        return [AllowAny()]

    @required_params(params=["tweet_id"])
    def list(self, request, *args, **kwargs):
        if "tweet_id" not in request.query_params:
            return Response(
                {
                    "message": "missing tweet_id in request",
                    "success": False,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        tweet_id = request.query_params["tweet_id"]
        comments = Comment.objects.filter(tweet_id=tweet_id)
        serializer = CommentSerializer(
            comments, context={"request": request}, many=True
        )
        return Response({"comments": serializer.data}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        data = {
            "user_id": request.user.id,
            "tweet_id": request.data.get("tweet_id"),
            "content": request.data.get("content"),
        }
        # 注意这里必须要加 'data=' 来指定参数是传给 data 的
        # 因为默认的第一个参数是 instance
        serializer = CommentSerializerForCreate(data=data)
        if not serializer.is_valid():
            return Response(
                {
                    "message": "Please check input",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # save 方法会触发 serializer 里的 create 方法，点进 save 的具体实现里可以看到
        comment = serializer.save()
        NotificationService.send_comment_notification(comment)
        return Response(
            CommentSerializer(comment, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        comment = self.get_object()
        serializer = CommentSerializerForUpdate(
            instance=comment,
            data=request.data,
        )
        if not serializer.is_valid():
            return Response(
                {
                    "message": "Please check input",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        # save will trigger the serializer update method
        comment = serializer.save()
        return Response(
            CommentSerializer(comment, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        comment.delete()
        # DRF 里默认 destroy 返回的是 status code = 204 no content
        # 这里 return 了 success=True 更直观的让前端去做判断，所以 return 200 更合适
        return Response({"success": True}, status=status.HTTP_200_OK)
