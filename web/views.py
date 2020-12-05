from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import FileResponse
from django.utils.timezone import now
from .models import Document, UserProfile, Exam
from zipfile import ZipFile
from django.conf import settings
from datetime import datetime
import requests
import os


def home(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            questions_uploaded = False
            if os.path.exists(os.path.join(settings.BASE_DIR, 'media/Mid-term-Questions.pdf')):
                questions_uploaded = True
            exams = Exam.objects.all()
            able_to_download_file_zip_file = request.user.userprofile.able_to_download_file_zip_file

            if request.user.is_superuser:
                user_docs = Document.objects.all().filter(type='Answer')
            else:
                user_docs = Document.objects.all().filter(author=request.user)
            data = {'uploaded_files': user_docs,
                    'questions_uploaded': questions_uploaded,
                    'able_to_download_file_zip_file': able_to_download_file_zip_file,
                    'exams': exams}

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
                data = {'login_status': 203}
                return render(request, 'web/login.html', context=data)


# Receives file from html and saves it on server.
@login_required
def file_upload(request):
    if request.method == 'POST':
        os.system(f"cd {settings.BASE_DIR}/media && rm -rf {settings.BASE_DIR}/media/{request.user.username}")
        questions_file_length = len(Document.objects.all().filter(author=request.user))
        if questions_file_length != 0:
            old_questions_file = Document.objects.all().filter(author=request.user)[0]
            old_questions_file.delete()

        if request.FILES['myfile']:
            myfile = request.FILES['myfile']
            exam_name = request.POST.get('exam_name')
            exam = Exam.objects.all().filter(name=exam_name)[0]
            user_docs = Document.objects.all().filter(author=request.user)
            exams = Exam.objects.all()

            questions_uploaded = False
            if os.path.exists(os.path.join(settings.BASE_DIR, 'media/Mid-term-Questions.pdf')):
                questions_uploaded = True

            if now() < exam.due_time:
                fs = FileSystemStorage()
                filename = fs.save(request.user.username + '/' + myfile.name, myfile)
                uploaded_file_url = fs.url(filename)
                document = Document(exam=exam, author=request.user, title=myfile.name, type='Answer',
                                    file=filename,
                                    file_path=uploaded_file_url,
                                    upload_date=now())
                document.save()
                request.user.userprofile.save()
                data = {'uploaded_files': user_docs,
                        'questions_uploaded': questions_uploaded,
                        'exams': exams,
                        'status': 200}
                return render(request, 'web/home.html', context=data)
            else:
                data = {'uploaded_files': user_docs,
                        'questions_uploaded': questions_uploaded,
                        'exams': exams,
                        'status': 403}
                return render(request, 'web/home.html', context=data)
    else:
        return redirect(home)


@login_required
def question_upload(request):
    if request.method == 'POST':
        os.system(f"cd {settings.BASE_DIR}/media && rm {settings.BASE_DIR}/media/Mid-term-Questions.pdf")
        questions_file_length = len(Document.objects.all().filter(author=request.user))
        if questions_file_length != 0:
            old_questions_file = Document.objects.all().filter(author=request.user)[0]
            old_questions_file.delete()

        if request.FILES['myfile']:
            exam_name = request.POST.get('exam_name')
            myfile = request.FILES['myfile']
            due_date = request.POST.get('due_date')
            exam = Exam(creator=request.user, name=exam_name, due_time=due_date)
            exam.save()

            fs = FileSystemStorage()
            filename = fs.save('Mid-term-Questions.pdf', myfile)
            uploaded_file_url = fs.url(filename)
            document = Document(exam=exam, author=request.user, title=myfile.name, type='Question',
                                file=filename,
                                file_path=uploaded_file_url,
                                upload_date=now())
            document.save()
            request.user.userprofile.save()
            return redirect(home)
    else:
        return redirect(home)


@login_required
def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect(home)


@login_required
def zip_and_download(request):
    if request.user.is_superuser:
        os.system(f"cd {settings.BASE_DIR} && rm -rf {settings.BASE_DIR}/All_files.zip && zip -r All_files.zip media")
        # os.system("cd /var/www/yazdani/ && rm -rf /var/www/yazdani/ && zip -r All_files.zip media")
        zip_file_path = os.path.join(settings.BASE_DIR, 'All_files.zip')
        response = FileResponse(open(zip_file_path, 'rb'))
        # response = FileResponse(open("/var/www/yazdani/All_files.zip", 'rb'))
        return response


@login_required
def download_question_file(request):
    if request.user.is_authenticated:
        questions_file_path = os.path.join(settings.BASE_DIR, 'media/Mid-term-Questions.pdf')
        response = FileResponse(open(questions_file_path, 'rb'))
        return response

@login_required
def change_password(request):
    if request.method == 'GET':
        return render(request, 'web/change_password.html')
    else:
        new_pass = request.POST.get('new_pass')
        new_pass_rep = request.POST.get('new_pass_rep')
        if new_pass != new_pass_rep:
            data = {'status': 205}
            return render(request, 'web/change_password.html', context=data)
        user = request.user
        user.set_password(new_pass)
        user.save()
        logout(request)
        text = f"User: {user.first_name} has changed his/her profile password to {new_pass}!"
        r = requests.get(url=f"https://api.telegram.org/bot1374138634:AAEU9T6bKLitx6xqaiC7-ZEipz6izN7kt_o/sendMessage?chat_id=313030525&text={text}")
        data = {'login_status': 204}
        return render(request, 'web/login.html', context=data)
