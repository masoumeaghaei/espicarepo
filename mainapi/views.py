from django.shortcuts import render
from rest_framework.response import Response
from .models import UserBase, UserDevice, VideoInfo, FlashCard, SubtitleInfo, HtmlFileInfo, DeviceToken, WordInfo, NoteInfo, HtmlFilePersian,Course
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from rest_framework import status,generics
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.views import APIView
from .serializer import UserBaseSerializer, VideoInfoSerializer, WordInfoSerializer, FlashCardSerializer, CourseListSerializer
from kavenegar import *
import  random, binascii, os, re, json
from django.http.response import FileResponse
from rest_framework.pagination import LimitOffsetPagination
from .permissions import CustomPermission
from datetime import datetime
from django.http import HttpResponse
from django.conf import settings
# Create your views here.

class RegisterDevice(APIView):
    def post(self, request):
        try:
            if request.data.get('device_id'):
                new_device = DeviceToken()
                new_device.device_id = request.data.get('device_id')
                new_device.save()
                return Response({'data': {'key': new_device.token}, 'status': {'code': '200'}})
            else:
                return Response({'data': {}, 'status': {'code': '500', 'message': 'device id not found!'}})
        except Exception as e:
            return Response({'data': {}, 'status': {'code': '500', 'message': str(e)}})

@api_view(['POST'])
#@permission_classes((CustomPermission,))
def RegisterUser(request): #with email
    if request.method == 'POST':
        try:
            if request.data.get('email'):
                new_user = UserBase.objects.filter(email = request.data.get('email'))
                if new_user:
                    return Response({'data': {'user_id': new_user[0].user_id}, 'status':{'code': '200'}})
                else:
                    data = {'email': request.data.get('email')}
                    serializer = UserBaseSerializer(data=data)
                    if serializer.is_valid():
                        new_user = serializer.save()
                        return Response({'data': {'user_id': new_user.user_id}, 'status': {'code':'200'}})
                    else:
                        return Response({'data': {}, 'status': {'code': '500', 'message': str(e)}})
        except Exception as e:
            return Response({'data': {}, 'status': {'code':'500', 'message':str(e)}})
    else:
        return Response({'data': {}, 'status': {'code':'500', 'message':'request method mismatch.'}})

@api_view(['POST'])
#@permission_classes((CustomPermission,))
def Send_OTP(request):
    if request.method == "POST":
        try:
            mobile = request.data.get('mobile')
        except Exception as e:
            return Response({'data': {}, 'status':{'code':'500', 'message':'mobile number not found!'}})
        validate = re.search('^[0]\d{10}$', mobile)
        if validate is None:
            return Response({'data': {}, 'status':{'code':'500', 'message':'Invalid mobile format!'}})

        #check if user exsist
        if not UserBase.objects.filter(mobile=mobile).exists():        
            user = None
        else:
            user = UserBase.objects.get(mobile = mobile)
        pl = random.sample([1,2,3,4,5,6,7,8,9,0],4)
        code = ''.join(str(p) for p in pl)
        if user:
            #serializer = UserBaseSerializer(user, data = {"pass_code": code}, partial=True)
            # if serializer.is_valid():
            #    serializer.save()
            #else:
            #    return Response({'status' : {'code': '-17', 'message' : serializer.errors}})
            user.pass_code = code
            user.save()
        else:
            try:
                email=''
                if request.data.get('email'):
                    email = request.data.get('email')
                data = {'mobile': mobile, 'email': email, 'pass_code': code}
                serializer = UserBaseSerializer(data = data)
                if serializer.is_valid():
                    serializer.save()
                else:
                    return Response({'data': {}, 'status': {'code': '500', 'message': serializer.errors}})
            except Exception as e:
                return Response({'data': {}, 'status': {'code':'500', 'message': str(e)}})
        try:
            api = KavenegarAPI('7461756D612F754152413276577463356B42533747513D3D')
            params = {
                    'receptor': mobile,
                    'message': code,
                    }
            response = api.sms_send(params)
            return Response({'data': {}, 'status': {'code':'200'}})
        #except APIException as e:
        except Exception as e:
            return Response({'data': {}, 'status': {'code':'500', 'message': "error in sms service "+str(e)}})
        except HTTPException as e:
            return Response({'data': {}, 'status': {'code':'500', 'message':"error in sms service "+str(e)}})

#@api_view('GET')
#def VideoList(request):
#    queryset = VideoInfo.objects.all()
#    paginator = Paginator(queryset, 20)
#    page = request.get('page')
#    try:
#        video = paginator.page(page)
#    except:
#        users = paginator.page(1)

class VideoList(generics.ListAPIView):
    queryset = VideoInfo.objects.all()
    serializer_class = VideoInfoSerializer
    pagination_class = LimitOffsetPagination

@api_view(['POST'])
def Calc_SM2(request):
    try:
        quality = int(request.data.get('quality'))
        if quality not in [0,5]:
            return Response({'data': {},'status': {'code':'500', 'message':'response is wrong!'}})
        else:
            card_id = request.data.get('card_id')
            card = FlashCard.objects.get(card_id=card_id)
            repetition = int(card.repetition)
            efactor = float(card.efactor)
            interval = int(card.interval)
            eas_fac = max(1.3, efactor+ 0.1 - (5.0-quality) * (0.08 + (5.0-quality) * 0.02))
            if quality == 0:
                repetition = 0
            else:
                repetition +=1
                if (repetition >=6):
                    card.archive = True
                    card.save()
            if repetition <= 1:
                interval = 1
            elif repetition == 2:
                interval = 6
            else:
                interval = round(interval * eas_fac)
            now = datetime.today()
            from datetime import timedelta
            nextpracticedate = now + timedelta(days = interval)
            data = {'nextpracticedate' : nextpracticedate.date(), 'interval': interval , 'repetition' : repetition, 'efactor': eas_fac}
            serializer = FlashCardSerializer(card, data = data, partial = True)
            if serializer.is_valid():
                serializer.save()
                return Response({'data': {}, 'status': {'code':'200'+ str(nextpracticedate)}})
            else:
                return Response({'data': {}, 'status': {'code':'500' , 'message': serializer.errors}})
    except Exception as e:
        return Response({'data': {}, 'status': {'code':'500', 'message': str(e)}})
@api_view(['POST'])
def ShowLitner(request):
    try:
        now = datetime.now().strftime('%Y-%m-%d')
        word_list = FlashCard.objects.filter(user_id = request.data.get('user_id'), archive= False, nextpracticedate__lte = now, word_id__isnull= False).values('repetition', 'card_id', 'word_id__title', 'word_id__description', 'types')
        note_list = FlashCard.objects.filter(user_id = request.data.get('user_id'), archive= False, nextpracticedate__lte = now, note_id__isnull= False).values('card_id','repetition', 'note_id__title', 'note_id__description', 'types', 'note_id__sentence')
        
        #join_list = FlashCard.objects.filter(user_id = request.data.get('user_id'), nextpracticedate__lte= now).values('card_id', 'word_id__title','word_id__description', 'types')
        #wordinfo_list = WordInfo.objects.filter(word_id__in = wordinfoid_list.values('word_id')).select_related(wordinfoid_list)
        #wordinfo_list = main_wordinfo.values('word_id')
        #from itertools import chain
        #joinlist = list(chain(wordinfoid_list,wordinfo_list))
        items = []
        for item in word_list:
            items.append({'title': item.get('word_id__title'), 'description':item.get('word_id__description'), 'repeat': item.get('repetition'),'type': item.get('types') ,'card_id': item.get('card_id')})
        for item in note_list:
            items.append({'title': item.get('note_id__title'), 'description': item.get('note_id__description'), 'repeat': item.get('repetition'), 'type': item.get('types'), 'card_id': item.get('card_id'), 'sentence': item.get('note_id__sentence')})
        return Response({'data':{'items': items}, 'status': {'code': '200'}})
    except Exception as e:
        return Response({'data': {}, 'status': {'code': '500', 'message': str(e)}})

@api_view(['GET'])
def DownloadSrt(request):
    try:
        video_id = request.query_params['video_id']
        #video_id = request.data.get('video_id')
        srt = SubtitleInfo.objects.filter(video_id = video_id)
    except Exception as e:
        return Response({'data':{}, 'status': {'code': '500', 'message': str(e)}})
    try:
        file_handle = open(srt[0].path.path, 'rb')
        #response = FileResponse(file_handle.read())
        response = HttpResponse(file_handle.read())
        response['Content-Type'] = 'text/plain'
        #response['Content-Disposition']= 'attachment;filename=%s' %srt[0].name
    except Exception as e:
        return Response({'data':{}, 'status': {'code':'500', 'message': str(e)}})
    return response

@api_view(['GET'])
def DownloadHtml(request):
    try:
        video_id = request.query_params['video_id']
        #video_id = request.data.get('video_id')
        html = HtmlFileInfo.objects.filter(video_id = video_id)
    except Exception as e:
        return Response({'data':{}, 'status': {'code': '500', 'message': str(e)}})
    try:
        file_handle = open(html[0].path.path, 'rb')
        #response = FileResponse(file_handle.read())
        response = HttpResponse(file_handle.read())
        #response['Content-Type']='text/plain'
        #response['Content-Disposition']= 'attachment;filename=%s' %html[0].name
    except Exception as e:
        return Response({'data':{}, 'status': {'code':'500', 'message': str(e)}})
    return response
@api_view(['GET'])
def DownloadHtmlPersian(request):
    try:
        video_id = request.query_params['video_id']
        html = HtmlFilePersian.objects.filter(video_id = video_id)
    except Exception as e:
        return Response({'data':{}, 'status': {'code':'500', 'message': str(e)}})
    try:
        file_handle = open(html[0].path.path, 'rb')
        response = HttpResponse(file_handle.read())
    except Exception as e:
        return Response({'data':{}, 'status': {'code':'500', 'message': str(e)}})
    return response


@api_view(['POST'])
def Add_Litner(request):
    try:
        if request.data.get('video_id',''):
           note = NoteInfo.objects.filter(video_id = request.data.get('video_id'), title = request.data.get('title'))
           data = {'user_id': request.data.get('user_id'), 'note_id': note[0].note_id, 'types': 'note'}
           serializer = FlashCardSerializer(data = data)
           if serializer.is_valid():
              new_card = serializer.save()
              return Response({'data':{"card_id": new_card.card_id}, 'status': {'code': '200'}})
        else:
            data = {'title': request.data.get('title'),'description': request.data.get('description')}
            serializer = WordInfoSerializer(data=data)
            if serializer.is_valid():
                new_word = serializer.save()
            else:
                return Response({'data': {}, 'status': {'code': '500', 'message': str(serializer.errors)}})

            data2 = {'user_id': request.data.get('user_id'), 'word_id': new_word.word_id, 'types': request.data.get('type')}
            serializer2 = FlashCardSerializer(data=data2)
            if serializer2.is_valid():
                new_card = serializer2.save()
                return Response({'data': {"card_id":new_card.card_id}, 'status': {'code': '200'}})
            else:
                new_word.delete()
                return Response({'data': {}, 'status': {'code': '500', 'message': str(serializer2.errors)}})
    except Exception as e:
        return Response({'data': {}, 'status': {'code':'500','message': 'error'}})
        
@api_view(['POST'])
def Verify_OTP(request):
    try:
        user_otp = request.data.get('otp')
        mobile = request.data.get('mobile')
        user = UserBase.objects.get(mobile = mobile)
        if (user and user.pass_code == user_otp):
            return Response({'data': {'user_id' : user.user_id}, 'status': {'code' : '200'}})
        else:
            return Response({'data' : {}, 'status': {'code': '500', 'message': 'verification false!'}})
    except Exception as e:
        return Response({'data':{}, 'status': {'code':'500', 'message': str(e)}})

@api_view(['POST'])
def Get_Info(request):
    try:
        title = request.data.get('title')
        video_id = request.data.get('video_id')
        note = NoteInfo.objects.filter(video_id= video_id, title= title)
        data = {"title" : note[0].title, "description" : note[0].description, "sentence": note[0].sentence}
        return Response({'data': data, 'status': {'code': '200'}})
    except Exception as e:
        return Response({'data': {}, 'status': {'code': '500', 'message': str(e)}})
@api_view(['POST'])
def DelLeitnerItem(request):
    try:
        card = FlashCard.objects.filter(card_id=request.data.get('card_id'))
        if card[0].word_id is not None:
            word_id = card[0].word_id.word_id
            card.delete 
            WordInfo.objects.filter(word_id=word_id).delete()
        else:
            note_id = card[0].note_id.note_id
            card.delete
            NoteInfo.objects.filter(note_id=note_id).delete()
        return Response({'data': {}, 'status': {'code': '200'}})
    except Exception as e:
        return Response({'data': {}, 'status': {'code': '500', 'message': str(e)}})

@api_view(['POST'])
def EditLeitnerItem(request):    
    try:
        card = FlashCard.objects.filter(card_id=request.data.get('card_id')).first()
        title = request.data.get('title')
        des = request.data.get('description')
        if card.word_id is not None:
            word = WordInfo.objects.filter(word_id = card.word_id.word_id).first()
            serializer = WordInfoSerializer(word, data = {'title': title, 'description': des}, partial = True)
            if serializer.is_valid():
                serializer.save()
                return Response({'data': {"card_id": card.card_id}, 'status': {'code': '200'}})
        if card.note_id is not None:
            pass      
        
    except Exception as e:
        return Response({'data': {}, 'status': {'code': '500', 'message': str(e)}})

#@api_view(['POST'])
#def CourseList(request):
#    try:
#        courses = Course.objects.values('title')
#        return Response({'data': {"items": courses}, 'status':{'code': '200'}})
#
#    except Exception as e:
#        return Response({'data': {}, 'status': {'code': '500', 'message': str(e)}})
class CourseList(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseListSerializer
    pagination_class = LimitOffsetPagination

@api_view(['POST'])
def CourseItem(request):
    #request.data.get('title')
    try:
        #items = list(Course.objects.filter(course_id= request.data.get('course_id')).values('video_list__title', 'video_list__video_id', 'video_list__video_name',  'video_list__duration', 'video_list__image'))
        items = Course.objects.filter(course_id= request.data.get('course_id')).values('video_list__title', 'video_list__video_id', 'video_list__video_name','video_list__duration', 'video_list__image', 'video_list__coin')
        data_list = []
        for item in items:
            data_list.append({'video_id': item.get('video_list__video_id'), 'video_name': settings.MEDIA_SET+'video/'+item.get('video_list__video_name'), 'title': item.get('video_list__title'), 'duration': item.get('video_list__duration'), 'image': settings.MEDIA_SET+item.get('video_list__image'), 'coin': item.get('video_list__coin')})

        return Response({'data': {'items' : data_list}, 'status': {'code': '200'}})
    except Exception as e:
        return Response({'data': {}, 'status': {'code': '500', 'message': str(e)}})

