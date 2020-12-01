from django.conf.urls import url
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    url('^$', views.home, name='home'),
    url('^logout$', views.logout_user, name='logout'),
    url('^home/$', views.home, name='home'),
    url('^home/upload_file/$', views.file_upload, name='file_upload'),
    url('^home/load_history/$', views.load_history, name='load_history'),
    url('^home/upload_file/load_history/$', views.load_history, name='load_history'),
    url('terms_and_conditions/$', views.auth_tc, name='auth_tc'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)