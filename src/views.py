from django.shortcuts import render, redirect
from django.views.generic import View, CreateView, ListView
from django.core.files.storage import FileSystemStorage
from .forms import Importdataform
from .models import Audio
import docx
from django.core.files import File
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
def modify_text(text):
    text = text.replace('.', '<break time="1s"/> ')
    return text


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
        scanned_text = ''
        page = convert_from_path(filename, 400)
        for i, image in enumerate(page):
            fname = "pdf" + str(i) + ".png"
            image.save(fname, "PNG")
            img = cv2.imread(fname)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            cv2.medianBlur(img, 3)
            scanned_text = pytesseract.image_to_string(img, lang='ara')
        #     scanned_text = modify_text(scanned_text)
        #     scanned_text = scanned_text.replace("'", " <break time='2s'/> ")
        #     # text = "<speak><prosody rate='x-slow'>{}</prosody><speak>".format(text)
        #     string_length = len(scanned_text) - 1
        #     text = '''
        #     <speak><prosody rate='slow'>{}</prosody></speak>
        #     '''.format(scanned_text[:string_length])
        #     print(text)
        # session = Session(aws_access_key_id='AKIAU4GHOSL2IRP4DI5R',
        #                   aws_secret_access_key='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',
        #                   region_name='us-east-2')
        # polly = session.client("polly")
        try:
            #     response = polly.synthesize_speech(
            #         OutputFormat="mp3",
            #         LanguageCode='arb',
            #         VoiceId="Zeina",
            #         TextType='ssml',
            #         Text=str(text)
            #     )

            x = self.model.objects.all().last()
            y = x.id
            # print('--------------------------------', y)
            # y = 1
            # y = str(y)
            # file = open('speech{}.mp3'.format(y), 'wb')
            # file.write(response['AudioStream'].read())
            # file.close()
            # audio_file = '/speech{}.mp3'.format(y)
            # # audio_file = '../../speech.mp3'
            # mydoc = docx.Document()
            # mydoc.add_paragraph(scanned_text)
            # mydoc.save("doc.docx")
            output = open('output{}.txt'.format(y), 'w', encoding='utf-8')
            # print(text.decode('utf-8'))
            # text = text.decode('utf-8')
            output.write(scanned_text)
            output.close()
            txt_file = '../../output{}.txt'.format(y)
            Audio.objects.create(
                audio=txt_file
            )
            # return HttpResponse("Created audio file")
            # os.remove(audio_file)
            # os.remove(filename)
            return redirect('src:list-view')
        except Exception as e:
            print(e)
            return HttpResponse(e)


class ListAudio(ListView):
    model = Audio
    template_name = 'audio.html'


class DownloadFile(View):
    model = Audio

    def get(self, request, *args, **kwargs):
        txt_file = Audio.objects.get(pk=self.kwargs.get('pk'))
        print(txt_file.audio)
        input_file = str(txt_file.audio).split('/')
        print(input_file)
        response = HttpResponse(open(str(input_file[2]), 'rb').read())
        response['Content-Type'] = 'text/plain'
        response['Content-Disposition'] = 'attachment; filename=output{}.txt'.format(txt_file.id)
        return response
