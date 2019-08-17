from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
import binascii, os
from datetime import datetime
from datetime import timedelta

# Create your models here.
class DeviceToken(models.Model):
    device_id = models.CharField(max_length = 50, primary_key = True)
    token = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add = True)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_key()
        return super().save(*args, **kwargs)
    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

class UserBase(models.Model):
    user_id = models.AutoField(primary_key = True)
    mobile = models.CharField(max_length=11, blank = True)
    email = models.CharField(max_length = 30, blank = True)
    pass_code = models.CharField(max_length = 5, blank = True)

class UserDevice(models.Model):
    user_id = models.ForeignKey(UserBase, on_delete = models.CASCADE)
    device_id = models.CharField(max_length = 30)
    status = models.CharField(max_length = 10)

class VideoInfo(models.Model):
    video_id = models.AutoField(primary_key = True)
    title = models.CharField(max_length = 50, default = 'title1')
    video_name = models.CharField(max_length = 60)
    path = models.FileField(upload_to = 'video', blank = True)
    duration = models.CharField(max_length = 20, default = '00:00:00')
    image = models.ImageField(upload_to = 'pic', blank = True)

class SubtitleInfo(models.Model):
    subtitle_id = models.AutoField(primary_key = True)
    video_id = models.ForeignKey(VideoInfo, on_delete = models.CASCADE)
    name = models.CharField(max_length = 60)
    path = models.FileField(upload_to = 'srt')

class HtmlFilePersian(models.Model):
    htmlfile_id = models.AutoField(primary_key = True)
    video_id = models.ForeignKey(VideoInfo, on_delete = models.CASCADE)
    name = models.CharField(max_length = 60)
    path = models.FileField(upload_to = 'htmlpersian')

class HtmlFileInfo(models.Model):
    htmlfile_id = models.AutoField(primary_key = True)
    video_id = models.ForeignKey(VideoInfo, on_delete = models.CASCADE)
    name = models.CharField(max_length = 60)
    path = models.FileField(upload_to = 'html')

class WordInfo(models.Model):
    word_id = models.AutoField(primary_key = True)
    title = models.CharField(max_length = 100)
    description = models.TextField(blank = True)

class NoteInfo(models.Model):
    note_id = models.AutoField(primary_key = True)
    title = models.CharField(max_length = 100)
    sentence = models.TextField(blank = True)
    description = models.TextField(blank = True)
    voice = models.FileField(upload_to = 'voice', blank = True, null = True)
    video_id = models.ForeignKey(VideoInfo, on_delete = models.CASCADE)

class FlashCard(models.Model):
    card_id = models.AutoField(primary_key = True)
    word_id = models.ForeignKey(WordInfo, on_delete = models.CASCADE, null = True, blank = True)
    note_id = models.ForeignKey(NoteInfo, on_delete = models.CASCADE, null = True, blank = True)
    user_id = models.ForeignKey(UserBase, on_delete = models.CASCADE)    
    repetition = models.IntegerField(default=0, blank = True)
    interval = models.IntegerField(default=0, blank = True)
    efactor = models.FloatField(default=2.5, blank = True)
    nextpracticedate = models.DateField(default= (datetime.now()+timedelta(days=1)).strftime('%Y-%m-%d'))
    create_date = models.DateField(default = datetime.now().strftime('%Y-%m-%d'))
    types = models.CharField(max_length = 60, default = 'word')
