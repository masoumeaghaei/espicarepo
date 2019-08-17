from django.contrib import admin
from .models import VideoInfo, SubtitleInfo, HtmlFileInfo, WordInfo, FlashCard, NoteInfo, HtmlFilePersian

# Register your models here.

admin.site.register(VideoInfo)
admin.site.register(SubtitleInfo)
admin.site.register(HtmlFileInfo)
admin.site.register(WordInfo)
admin.site.register(FlashCard)
admin.site.register(NoteInfo)
admin.site.register(HtmlFilePersian)
