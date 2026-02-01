from django.db import models
from django.contrib.auth.models import User

# This stores the file uploads
class EquipmentData(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

# This stores the Extra User Details (Phone, Institute, etc.)
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    institute = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=15)
    college_id = models.CharField(max_length=50)
    dob = models.CharField(max_length=20)
    security_pin = models.CharField(max_length=10)

    def __str__(self):
        return self.user.username