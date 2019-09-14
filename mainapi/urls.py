#urls.py
from django.conf.urls import include
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from .views import (RegisterUser, VideoList, DownloadSrt, DownloadHtml, Send_OTP,
        RegisterDevice, Add_Litner, ShowLitner, Calc_SM2, Verify_OTP, DownloadHtmlPersian,
        Get_Info, DelLeitnerItem, EditLeitnerItem, CourseList, CourseItem)

urlpatterns = [
        path('register/user/',RegisterUser, name = 'register_user'),
        path('video/list/',VideoList.as_view(), name= 'VideoList'),
        path('srt/download/', DownloadSrt, name= 'DownloadSrt'),
        path('html/download/', DownloadHtml, name= 'DownloadHtml'),
        path('send/otp/', Send_OTP, name= 'SendOTP'),
        path('register/device/',RegisterDevice.as_view(), name= 'RegisterDevice'),
        path('add/flashcard/', Add_Litner, name = 'AddFlashcard'),
        path('show/litner/', ShowLitner, name= 'ShowLitner'),
        path('flashcard/review/', Calc_SM2, name = 'ReviewFlashcard'),
        path('verify/otp/', Verify_OTP, name = 'Verify_OTP'),
        path('html/persian/download/', DownloadHtmlPersian, name = 'DownloadHtmlPersion'),
        path('get/info/', Get_Info, name = 'GetInfo'),
        path('del/leitner/', DelLeitnerItem, name= 'DeleteLeitner'),
        path('edit/leitner/', EditLeitnerItem, name= 'EditLeitner'),
        path('course/list/', CourseList.as_view(), name= 'courselist'),
        path('course/item/', CourseItem, name= 'coursedetail')
]
