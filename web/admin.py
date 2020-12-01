from django.contrib import admin
from .models import UserProfile, Document

admin.site.register(UserProfile)
admin.site.register(Document)