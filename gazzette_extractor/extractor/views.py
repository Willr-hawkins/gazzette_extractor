from django.shortcuts import render
from .forms import FileUploadForm

def upload_file(request):
    """ Handle upload file form submissions """

    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return render(request, 'extractor/success.html')
    else:
        form = FileUploadForm()
    return render(request, 'extractor/upload.html', {'form': form})
