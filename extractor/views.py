from django.shortcuts import render
from .forms import FileUploadForm
import os
from django.conf import settings
from django.http import HttpResponse

import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import spacy
from langdetect import detect
import json

# Load spaCy models
nlp_en = spacy.load('en_core_web_sm')
nlp_fr = spacy.load('fr_core_news_sm')
nlp_nl = spacy.load('nl_core_news_sm')

def upload_file(request):
    """ Handle upload file form submissions """

    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload_file = form.save()
            file_path = os.path.join(settings.MEDIA_ROOT, upload_file.file.name)
            extracted_info = process_file(file_path)
            
            # Create json file
            json_data = json.dumps(extracted_info, indent=4)
            json_filename = f"{upload_file.file.name}_extracted_data.json"
            json_file_path = os.path.join(settings.MEDIA_ROOT, json_filename)

            # Write json file
            with open(json_file_path, 'w') as json_file:
                json_file.write(json_data)
            
            json_file_url = os.path.join(settings.MEDIA_URL, json_filename)
            return render(request, 'extractor/success.html', {'json_file_url': json_file_url})
    else:
        form = FileUploadForm()
    return render(request, 'extractor/upload.html', {'form': form})

def process_file(file_path):
    """ Process the upload file using Terrseract """

    if file_path.endswith('.pdf'):
        images = convert_from_path(file_path)
        image = images[0]
    else:
        image = Image.open(file_path)
    
    # Perform OCR on the image
    text = pytesseract.image_to_string(image)

    extracted_info = process_text(text)

    return extracted_info

def process_text(text):
    """ Process the extracted text from the OCR process """

    language = detect(text)

    # Choose the appropriate spaCy model for the correct language
    if language == 'en':
        nlp = nlp_en
    elif language == 'fr':
        nlp = nlp_fr
    elif language == 'nl':
        nlp = nlp_nl
    else:
        nlp = nlp_en
    
    doc = nlp(text)

    # Extract the required entities
    entities = {
        'company_name': [],
        'company_identifier': [],
        'document_purpose': [],
    }

    # Iterate through the extracted entities and add them to the relevant fields
    for ent in doc.ents:
        if ent.label_ == 'ORG':
            entities['company_name'].append(ent.text)
        elif ent.label_ == 'DATE':
            entities['document_purpose'].append(ent.text)  # Fixed the typo here
        elif ent.label_ == 'PRODUCT':
            entities['company_identifier'].append(ent.text)
    
    return entities