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

class Exam(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=128)
    due_time = models.DateTimeField(default=now)

    def __str__(self):
        return "{}-{}".format(self.name, self.due_time)

# User uploaded documents
class Document(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='media/')
    file_path = models.CharField(max_length=100, default='media/')
    upload_date = models.DateTimeField(default=now)

    answer = 'Answer'
    question = 'Question'

    type_choices = (
        (answer, 'Answer'),
        (question, 'Question'),
    )

    type = models.CharField(blank=True, choices=type_choices, default=question, max_length=64)

    def __str__(self):
        return "{}-{}-{}-{}".format(self.type, self.author.username, self.title, self.upload_date)

# Creates a user profile after adding a user.
def create_profile(sender, **kwargs):
    if kwargs['created']:
        user_profile = UserProfile.objects.create(user=kwargs['instance'])


post_save.connect(receiver=create_profile, sender=User)