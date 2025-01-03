from django.shortcuts import render
from .forms import FileUploadForm
import os
from django.conf import settings

import pytesseract
from PIL import Image

def upload_file(request):
    """ Handle upload file form submissions """

    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload_file = from.save()
            file_path = os.path.join(settinmgs.MEDIA_ROOT, upload_file.file.name)
            extracted_text = process_file(file_path)
            return render(request, 'extractor/success.html', {'text': extracted_text})
    else:
        form = FileUploadForm()
    return render(request, 'extractor/upload.html', {'form': form})

def process_file(file_path):
    """ Process the upload file using Terrseract """

    image = Image.open(file_path)

    text = pytesseract.image_to_string(image)
    return text