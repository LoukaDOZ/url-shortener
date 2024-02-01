from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    username = models.CharField(db_column="username", max_length=32, primary_key=True)

    class Meta:
        db_table = "users"
    
    def __str__(self):
        return self.username

class URL(models.Model):
    _id = models.CharField(db_column="url_id", max_length=8, primary_key=True)
    target = models.CharField(db_column="target_url", max_length=512)
    expiration = models.BigIntegerField(db_column="expiration_date")
    username = models.ForeignKey("User", db_column="username", null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = "url"
    
    def __str__(self):
        return self._id