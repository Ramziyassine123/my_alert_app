# # models.py
#
# from django.db import models
# from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
#
#
# class UserManager(BaseUserManager):
#     def create_user(self, name, password=None):
#         if not name:
#             raise ValueError('Users must have a name')
#         user = self.model(name=name)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user
#
#     def create_superuser(self, name, password=None):
#         user = self.create_user(name, password)
#         user.is_admin = True
#         user.save(using=self._db)
#         return user
#
#
# class UserProfile(AbstractBaseUser):
#     name = models.CharField(max_length=255, unique=True)
#     is_active = models.BooleanField(default=True)
#     is_admin = models.BooleanField(default=False)
#
#     objects = UserManager()
#
#     USERNAME_FIELD = 'name'
#     REQUIRED_FIELDS = []
#
#     def __str__(self):
#         return self.name
#
#
# class Alert(models.Model):
#     user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='alerts')
#     title = models.CharField(max_length=255)
#     message = models.TextField()
#     notification_type = models.CharField(max_length=20)
#     period = models.IntegerField()
#
#     def __str__(self):
#         return self.title
#

from django.db import models


class FCMToken(models.Model):
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token
