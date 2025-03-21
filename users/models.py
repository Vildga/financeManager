from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email or email.strip() == "":
            raise ValueError("Email обов'язковий")
        email = self.normalize_email(email)
        extra_fields.pop("username", None)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    LANGUAGE_CHOICES = [
        ("en", "English"),
        ("uk", "Ukrainian"),
    ]

    THEME_CHOICES = [
        ("light", "Light"),
        ("dark", "Dark"),
    ]

    language = models.CharField(
        max_length=10, choices=LANGUAGE_CHOICES, default="en", verbose_name="Language"
    )
    theme = models.CharField(
        max_length=10, choices=THEME_CHOICES, default="light", verbose_name="Theme"
    )
    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
