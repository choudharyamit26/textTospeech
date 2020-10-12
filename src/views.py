from django.shortcuts import render, redirect
from django.views.generic import View, CreateView, ListView
from django.core.files.storage import FileSystemStorage
from .forms import Importdataform
from .models import Audio
from django.http import HttpResponseRedirect, HttpResponse
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import os
import sys
import subprocess
from tempfile import gettempdir
from io import StringIO
import boto3
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

from pdf2image import convert_from_path
import pytesseract
import argparse
import cv2
from PIL import Image


# Create your views here.


class CreateAudio(View):
    template_name = 'upload.html'
    model = Audio
    form_class = Importdataform

    def get(self, request, *args, **kwargs):
        return render(self.request, 'upload.html')

    def post(self, request, *args, **kwargs):
        in_file = self.request.FILES['document']
        fs = FileSystemStorage()
        filename = fs.save(in_file.name, in_file)
        text = ''
        arabic_text = []
        page = convert_from_path(filename, 400)
        for i, image in enumerate(page):
            print(image)
            fname = "pdf" + str(i) + ".png"
            image.save(fname, "PNG")
            img = cv2.imread(fname)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            cv2.medianBlur(img, 3)
            scanned_text = pytesseract.image_to_string(img, lang='ara')
            arabic_text.append(text)
            # print('>>>>>>>>>>>', arabic_text)
            # text = "<speak><prosody rate='slow'>{}</prosody></speak>".format(text)
            # text = "<speak>{}</speak>".format(text)
            # l = 'Alexa'
            print('--------------------------->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>', text)
            # l = 'أليكسا'
            # l = """
            #     هذه إحدى قصص ما قبل النوم الكلاسيكية للأطفال .تبدأ القصة في مزرعة » حيث تجلس بطة على مجموعة من البيض لجعلها
            #     تفقس .يفقس البيض واحدا تلو الآخر » وسرعان ما يكون هناك ستة فراخ بط صفراء الريش » تزقزق بحماس .تستغرق آخر بيضة وقتًا
            #     أطول حتى تفقس » ومن ثم تظهر بطة غريبة الشكل ذات ريش رمادي .الجميع يجد البطة الرمادية قبيحة » بما في ذلك والدتها .تهرب
            #     البطة المكتئبة وتعيش بمفردها في مستنقع حى يأتي الشتاء .عند رؤية البطة تتضور جوعًا في الشتاء » يشفق مزارع على البطة القبيحة
            #     .ويمنحها الطعام والمأوى في المنزل .ومع ذلك » فإن البطة تخاف من صخب أطفال المزارع وتهرب إلى كهف بجانب بحيرة متجمدة
            # """
            # l = """
            #     هذه إحدى قصص ما قبل النوم الكلاسيكية للأطفال .تبدأ القصة في مزرعة » حيث تجلس بطة على مجموعة من البيض لجعلهاهذه إحدى قصص ما قبل النوم الكلاسيكية للأطفال .تبدأ القصة في مزرعة » حيث تجلس بطة على مجموعة من البيض لجعلها
            #     تفقس .يفقس البيض واحدا تلو الآخر » وسرعان ما يكون هناك ستة فراخ بط صفراء الريش » تزقزق بحماس .تستغرق آخر بيضة وقتًا
            #     أطول حتى تفقس » ومن ثم تظهر بطة غريبة الشكل ذات ريش رمادي .الجميع يجد البطة الرمادية قبيحة » بما في ذلك والدتها .تهرب
            #     البطة المكتئبة وتعيش بمفردها في مستنقع حى يأتي الشتاء .عند رؤية البطة تتضور جوعًا في الشتاء » يشفق مزارع على البطة القبيحة
            #     .ويمنحها الطعام والمأوى في المنزل .ومع ذلك » فإن البطة تخاف من صخب أطفال المزارع وتهرب إلى كهف بجانب بحيرة متجمدة
            #
            #     » عندما يأتي الربيع » ينزل قطيع من البجع الجميل على البحيرة » ويقترب البطة » التي نمت بالكامل الآن » لكنها وحيدة » من البجع
            #     متوقعة تمامًا أن يتم رفضها .لدهشته » البجعات ترحب به .ينظر إلى انعكاس صورته في الماء ويدرك أنه لم يعد بطة قبيحة » بل بجعة
            #     .جميلة .ينضم البجعة إلى هذا القطيع ويطير مع عائلته الجديدة
            #
            #     قصة ميداس هي قصة كلاسيكية أخرى قبل النوم للأطفال .تصف هذه القصة القديمة من اليونان الملك ميداس بأنه رجل جشع
            #     وساخط » يحب الذهب أكثر من أي شيء آخر .مرة » قام بعمل صالح لشخص ما » وظهر أمامه إله يوناني » قائلاً إنه سيمنح رغبة قلبه
            #     للقيام بالعمل الصالح .تمنى ميداس أن يتحول كل شيء يلمسه إلى ذهب على الفور .وهب الله رغبته .كان ميداس متحمسًا للغاية وقام
            #     بلمس الأشياء العشوائية وتحويل كل شيء لمسه إلى ذهب .بعد فترة جاع .ومع ذلك » عندما لمس طعامه » تحول إلى ذهب » ولم
            #
            #     » يستطع أكله .كان يتضور جوعًا ويفزع لأنه لا يستطيع تناول الطعام .عندما رآه مضطرنا » ألقت ابنته المحببة ذراعيها حوله لتهدئته
            #     وتحولت أيضًا إلى الذهب .ارتاع ميداس أن ابنته أصبحت تمثالًّا من ذهب .ندم على طلب اللمسة الذهبية وأدرك أنه كان جشْعًا وأن
            #     الذهب لم يكن أثمن شيء في العالم .فبى وتوسل اللّه أن يتراجع عن رغبته أشفق عليه الله وطلب منه أن يغطس في النهر بجوار قصره
            #     ثم يملأ إبريقًا من الماء من النهر ويرشها على كل الأشياء التي يريد تغبيرها .اتبع التعليمات وأعاد ابنته إلى وضعها الطبيي .كان سعيدًا »
            #     .جدًا لاستعادة ابنته الحبيبة وتوقف عن الجشع منذ تلك اللحظة
            # """
            # l = """{}""".format(arabic_text[0])
            # l = text
            # print('Length---->>>',len(text))
            # print('<<<<<<<<<<<<<<<>>>>>>>>', scanned_text[:1903])
            # l = ''.join(text),
            # text = "<speak><prosody rate='x-slow'>{}</prosody><speak>".format(text)
            # text = "<speak><prosody rate='x-slow'>HI {}</prosody><speak>".format(l)
            string_length = len(scanned_text)-1
            # print('-----------------------------------',string_length)
            text = '''
            <speak><prosody rate='slow'>{}</prosody></speak>
            '''.format(scanned_text[:string_length])
            print(text)
        # print(in_file)
        # arabic_txt = ''
        # output_string = StringIO()
        # with open(uploaded_file, 'rb') as in_file:
        # a = []
        # parser = PDFParser(in_file)
        # doc = PDFDocument(parser)
        # codec = 'utf-8'
        # rsrcmgr = PDFResourceManager()
        # device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        # interpreter = PDFPageInterpreter(rsrcmgr, device)
        # for page in PDFPage.create_pages(doc):
        #     interpreter.process_page(page)
        # text = output_string.getvalue()
        # a = a.append(text)
        # arabic_txt = ''.join(text)
        # print(arabic_txt)
        # in_file.close()
        # device.close()
        # output_string.close()
        # text = text.encode('utf-8')
        # output = open('output.txt', 'wb')
        # print(text.decode('utf-8'))
        # text = text.decode('utf-8')
        # output.write(text)
        # output.close()
        # return text
        # print(text)

        session = Session(aws_access_key_id='AKIAU4GHOSL2LRH2BYHQ',
                          aws_secret_access_key='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',
                          region_name='us-east-2')
        # polly = boto3.client(service_name="polly", region_name='us-east-2', aws_access_key_id='AKIAU4GHOSL2LRH2BYHQ',
        #                      aws_secret_access_key='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', )
        polly = session.client("polly")
        try:
            # Request speech synthesis
            # {
            #     "Engine": "string",
            #     "LanguageCode": "string",
            #     "LexiconNames": ["string"],
            #     "OutputFormat": "string",
            #     "SampleRate": "string",
            #     "SpeechMarkTypes": ["string"],
            #     "Text": "string",
            #     "TextType": "string",
            #     "VoiceId": "string"
            # }

            response = polly.synthesize_speech(
                OutputFormat="mp3",
                LanguageCode='arb',
                VoiceId="Zeina",
                TextType='ssml',
                Text=str(text)
            )
            x = self.model.objects.all().last()
            y = ''
            y = x.id
            print('--------------------------------', y)
            y += 1
            y = str(y)
            file = open('speech{}.mp3'.format(y), 'wb')
            file.write(response['AudioStream'].read())
            file.close()
            audio_file = '/speech{}.mp3'.format(y)
            # audio_file = '../../speech.mp3'
            Audio.objects.create(
                audio=audio_file
            )
            # return HttpResponse("Created audio file")
            return redirect('src:list-view')
        except Exception as e:
            print(e)
            return HttpResponse(e)


class ListAudio(ListView):
    model = Audio
    template_name = 'audio.html'
