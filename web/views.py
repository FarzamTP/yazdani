from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import FileResponse
from django.utils.timezone import now
from .models import Document
from zipfile import ZipFile
from django.conf import settings
import os


def home(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            if request.user.is_superuser:
                user_docs = Document.objects.all()
            else:
                user_docs = Document.objects.all().filter(author=request.user)
            data = {'uploaded_files': user_docs}
            return render(request, 'web/home.html', context=data)
        else:
            return render(request, 'web/login.html')
    else:
        if request.user.is_authenticated:
            return render(request, 'web/home.html')
        else:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect(home)
            else:
                return HttpResponse("User not found!")


# Receives file from html and saves it on server.
@login_required
def file_upload(request):
    if request.method == 'POST':
        if request.FILES['myfile']:
            myfile = request.FILES['myfile']
            fs = FileSystemStorage()
            filename = fs.save(request.user.username + '/' + myfile.name, myfile)
            uploaded_file_url = fs.url(filename)
            document = Document(author=request.user, title=myfile.name,
                                file=filename,
                                file_path=uploaded_file_url,
                                upload_date=now())
            document.save()
            request.user.userprofile.save()
            return redirect(home)
    else:
        return redirect(home)

# Receives post request and sends back the user uploaded files.
@login_required
def load_history(request):
    if request.method == 'POST':
        if request.POST.get('request') == 'load_history_request':
            user_docs = Document.objects.all().filter(author=request.user).values()
            data = {
                'uploaded_files': list(user_docs)
            }
        else:
            data = {
                'uploaded_files': 'post'
            }
        return JsonResponse(data=data)

@login_required
def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect(home)

def zip_and_download(request):
    if request.user.is_superuser:
        file_path = os.path.join(settings.BASE_DIR, 'All_files.zip')
        os.system(f"rm -rf {file_path}")
        os.system(f"zip -r {file_path} media")
        response = FileResponse(open(file_path, 'rb'))
        return response


