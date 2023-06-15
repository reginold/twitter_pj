from django.contrib.auth.models import User
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from friendships.api import paginations
from friendships.api.serializers import (
    FollowerSerializer,
    FollowingSerializer,
    FriendshipSerializerForCreate,
)
from friendships.models import Friendship


class FriendshipViewSet(viewsets.GenericViewSet):
    serializer_class = FriendshipSerializerForCreate
    queryset = User.objects.all()
    # different view has the different paginaiton
    pagination_class = paginations.FriendshipPagination

    @action(methods=["GET"], detail=True, permission_classes=[AllowAny])
    def followers(self, request, pk):
        # GET /api/friendship/1/followers
        friendships = Friendship.objects.filter(to_user_id=pk).order_by("-created_at")
        page = self.paginate_queryset(friendships)
        serializer = FollowerSerializer(page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)

    def list(self, request):
        return Response({"message": "this is the message"})

    @action(methods=["GET"], detail=True, permission_classes=[AllowAny])
    def followings(self, request, pk):
        friendships = Friendship.objects.filter(from_user_id=pk).order_by("-created_at")
        page = self.paginate_queryset(friendships)
        serializer = FollowingSerializer(page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)

    @action(methods=["POST"], detail=True, permission_classes=[IsAuthenticated])
    def follow(self, request, pk):
        # You can also use following method to check the user exist or not
        # self.get_object()

        # /api/friendships/<pk>/follow/
        if Friendship.objects.filter(from_user=request.user, to_user=pk).exists():
            return Response(
                {
                    "success": True,
                    "duplicate": True,
                },
                status=status.HTTP_201_CREATED,
            )

        serializer = FriendshipSerializerForCreate(
            data={
                "from_user_id": request.user.id,
                "to_user_id": pk,
            }
        )
        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Please check the input.",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance = serializer.save()
        return Response(
            FollowingSerializer(instance, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    @action(methods=["POST"], detail=True, permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk):
        # raise the 404 if no user
        unfollow_user = self.get_object()

        # 注意 pk 的类型是 str，所以要做类型转换
        if request.user.id == unfollow_user.id:
            return Response(
                {
                    "success": False,
                    "message": "You cannot unfollow yourself",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        # https://docs.djangoproject.com/en/3.1/ref/models/querysets/#delete
        # Queryset 的 delete 操作返回两个值，一个是删了多少数据，一个是具体每种类型删了多少
        # 为什么会出现多种类型数据的删除？因为可能因为 foreign key 设置了 cascade 出现级联
        # 删除，也就是比如 A model 的某个属性是 B model 的 foreign key，并且设置了
        # on_delete=models.CASCADE, 那么当 B 的某个数据被删除的时候，A 中的关联也会被删除。
        # 所以 CASCADE 是很危险的，我们一般最好不要用，而是用 on_delete=models.SET_NULL
        # 取而代之，这样至少可以避免误删除操作带来的多米诺效应。
        deleted, _ = Friendship.objects.filter(
            from_user=request.user,
            to_user=pk,
        ).delete()
        return Response({"success": True, "deleted": deleted})
