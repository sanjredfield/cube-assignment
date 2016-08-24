from rest_framework import exceptions, mixins
from rest_framework import serializers, viewsets

from . import IsAuthenticatedAndRegistered
from ..models import UserProfile, UserVideo, Video
from ..tasks import update_credits


class BasicVideoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Video
        fields = ('url', 'id', 'created_at', 'name', 'description', 'credits', 'length')


class VideoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Video
        fields = (
            'url', 'id', 'created_at', 'name', 'description', 'youtube_id', 'credits', 'length'
        )


class FullVideoSerializer(serializers.HyperlinkedModelSerializer):
    user_video = serializers.SerializerMethodField()

    def get_user_video(self, video):
        user = self.context['request'].user
        try:
            uservideo = UserVideo.objects.get(user=user, video=video)
            return {
                'id': uservideo.id,
                'active': uservideo.active,
                'credits_awarded': uservideo.credits_awarded,
                'percent_watched': uservideo.percent_watched
            }
        except:
            return None

    class Meta:
        model = Video
        fields = (
            'url', 'id', 'created_at', 'name', 'description', 'youtube_id', 'credits', 'user_video'
        )


class UserVideoSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(view_name='userprofile-detail', read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=UserProfile.objects.all(), source='user')
    video = VideoSerializer(read_only=True)
    video_id = serializers.PrimaryKeyRelatedField(queryset=Video.objects.all(), source='video')

    class Meta:
        model = UserVideo
        read_only_fields = ('user', 'video', 'credits_awarded')
        fields = (
            'url', 'id', 'user', 'user_id', 'video', 'video_id', 'subscribed_at', 'length_watched',
            'active', 'credits_awarded', 'percent_watched'
        )


class VideoViewSet(mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    queryset = Video.objects.all().order_by('-created_at')
    serializer_class = BasicVideoSerializer
    permission_classes = ()

    def get_serializer_class(self):
        user = self.request.user
        if not user.is_anonymous() and user.valid_subscription:
            return FullVideoSerializer
        return BasicVideoSerializer


class UserVideoViewSet(viewsets.ModelViewSet):
    queryset = UserVideo.objects.all().order_by('-subscribed_at')
    serializer_class = UserVideoSerializer
    permission_classes = (IsAuthenticatedAndRegistered, )
    wrong_user_msg = 'You cannot subscribe to a video for this user.'
    subscribe_error_msg = 'You must have a valid subscription to do that!'

    def get_queryset(self):
        query = UserVideo.objects.filter(user=self.request.user)
        active = self.request.query_params.get('active', None)
        if active is not None:
            query = query.filter(active=active)
        pk = self.request.query_params.get('id', None)
        if pk is not None:
            query = query.filter(id=pk)
        return query

    def perform_create(self, serializer):
        curr_user_id = serializer.validated_data['user'].id
        if curr_user_id != self.request.user.id:
            raise exceptions.PermissionDenied(self.wrong_user_msg)
        if not self.request.user.valid_subscription:
            raise exceptions.PermissionDenied(self.subscribe_error_msg)
        serializer.save()

    def perform_update(self, serializer):
        curr_user_id = serializer.validated_data['user'].id
        if curr_user_id != self.request.user.id:
            raise exceptions.PermissionDenied(self.wrong_user_msg)
        if not self.request.user.valid_subscription:
            raise exceptions.PermissionDenied(self.subscribe_error_msg)

        uservideo = serializer.instance
        new_length_watched = serializer.validated_data['length_watched']
        if (uservideo.should_update_credits(new_length_watched)):
            update_credits.delay(uservideo.id)
        serializer.save()

    def perform_destroy(self, instance):
        raise exceptions.PermissionDenied('Deletes not permitted.')
