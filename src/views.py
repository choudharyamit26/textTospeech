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
        page = convert_from_path(filename, 400)
        for i, image in enumerate(page):
            print(image)
            fname = "pdf" + str(i) + ".png"
            image.save(fname, "PNG")
            img = cv2.imread(fname)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            cv2.medianBlur(img, 3)
            text = pytesseract.image_to_string(img, lang='ara')
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
        polly = session.client("polly")
        try:
            # Request speech synthesis
            response = polly.synthesize_speech(Text=text,
                                               OutputFormat="mp3",
                                               VoiceId="Zeina")
            x = self.model.objects.all().last()
            y = ''
            y = x.id
            print('--------------------------------',y)
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
