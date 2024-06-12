from django.db import models
from django.contrib.auth.models import AbstractUser

class UserDB(AbstractUser):
	# add business_id
	business_id = models.CharField(max_length=50, default="0000000000")
