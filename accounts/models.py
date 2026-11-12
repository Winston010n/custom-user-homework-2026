from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("У пользователя должен быть указан email.")
        if not username:
            raise ValueError("У пользователя должен быть указан username.")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("У суперпользователя is_staff должен быть True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("У суперпользователя is_superuser должен быть True.")

        return self.create_user(email, username, password, **extra_fields)


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Администратор"
        MODERATOR = "MODERATOR", "Модератор"
        USER = "USER", "Пользователь"
        CLIENT = "CLIENT", "Клиент"

    email = models.EmailField("email", unique=True)
    role = models.CharField(
        "роль",
        max_length=10,
        choices=Role.choices,
        default=Role.CLIENT,
    )
    bio = models.TextField("описание профиля", blank=True)
    birth_date = models.DateField("дата рождения", null=True, blank=True)
    is_verified = models.BooleanField("аккаунт подтвержден", default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email
