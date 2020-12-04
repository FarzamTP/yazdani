from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils.timezone import now

# User profile
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    able_to_download_file_zip_file = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

# User uploaded documents
class Document(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='uploaded_data')
    file_path = models.CharField(max_length=100, default='uploaded_data/')
    upload_date = models.DateTimeField(default=now)

    def __str__(self):
        return "{}-{}-{}".format(self.author.username, self.title, self.upload_date)

# Creates a user profile after adding a user.
def create_profile(sender, **kwargs):
    if kwargs['created']:
        user_profile = UserProfile.objects.create(user=kwargs['instance'])


post_save.connect(receiver=create_profile, sender=User)