#serializer
from rest_framework.serializers import ModelSerializer
from .models import UserBase, UserDevice, DeviceToken, VideoInfo, WordInfo, FlashCard, Course
from rest_framework import serializers
from django.conf import settings
class UserBaseSerializer(ModelSerializer):
    class Meta:
        model = UserBase
        fields = ('mobile', 'email')

class UserDeviceSerializer(ModelSerializer):
    class Meta:
        model = UserDevice
        fields = ('device_id','status')

class DeviceTokenSerializer(ModelSerializer):
    class Meta:
        model = DeviceToken
        fields = ('device_id', 'token', 'created')

class VideoInfoSerializer(ModelSerializer):
    image = serializers.SerializerMethodField('image_url')
    video_name = serializers.SerializerMethodField('video_url')
    def image_url(self, videoinfo):
        try:
            #request = self.context.get('request')
            image_url = videoinfo.image.url
            return (settings.MEDIA_SET + image_url)
        except:
            return ""
    def video_url(self, videoinfo):
        try:
            video_url = videoinfo.path.url
            return (settings.MEDIA_SET + video_url)
        except:
            return ""

    class Meta:
        model = VideoInfo
        fields = ('video_name', 'video_id', 'title', 'duration', 'image')

class CourseListSerializer(ModelSerializer):
    class Meta:
        model = Course
        fields = ('course_id', 'title')

class WordInfoSerializer(ModelSerializer):
    class Meta:
        model = WordInfo
        fields = ('title', 'description')

class FlashCardSerializer(ModelSerializer):
    class Meta:
        model = FlashCard
        fields = ('card_id','word_id','note_id' ,'user_id', 'repetition','interval','efactor','nextpracticedate', 'types')

