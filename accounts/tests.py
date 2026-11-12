from unittest.mock import patch

from django.contrib import admin
from django.contrib.auth import authenticate
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .admin import CustomUserAdmin
from .models import CustomUser


class CustomUserTests(TestCase):
    def test_user_defaults_and_optional_profile_fields(self):
        user = CustomUser.objects.create_user(
            email="client@example.com",
            username="client",
            password="secure-test-password",
        )

        self.assertEqual(user.role, CustomUser.Role.CLIENT)
        self.assertFalse(user.is_verified)
        self.assertEqual(user.bio, "")
        self.assertIsNone(user.birth_date)

    def test_superuser_manager_sets_required_permissions(self):
        user = CustomUser.objects.create_superuser(
            email="admin@example.com",
            username="admin",
            password="secure-test-password",
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_createsuperuser_management_command(self):
        with patch.dict("os.environ", {"DJANGO_SUPERUSER_PASSWORD": "secure-test-password"}):
            call_command(
                "createsuperuser",
                email="command-admin@example.com",
                username="command-admin",
                interactive=False,
                verbosity=0,
            )

        user = CustomUser.objects.get(email="command-admin@example.com")
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password("secure-test-password"))

    def test_email_authentication_and_admin_user_creation(self):
        admin_user = CustomUser.objects.create_superuser(
            email="admin@example.com",
            username="admin",
            password="secure-admin-password",
        )
        self.assertEqual(
            authenticate(email=admin_user.email, password="secure-admin-password"),
            admin_user,
        )

        self.client.force_login(admin_user)
        response = self.client.post(
            reverse("admin:accounts_customuser_add"),
            {
                "email": "new-client@example.com",
                "username": "new-client",
                "password1": "Strong!ClientPass902",
                "password2": "Strong!ClientPass902",
                "role": CustomUser.Role.CLIENT,
                "is_active": "on",
            },
        )

        self.assertEqual(response.status_code, 302)
        new_user = CustomUser.objects.get(email="new-client@example.com")
        self.assertEqual(new_user.role, CustomUser.Role.CLIENT)
        self.assertFalse(new_user.is_staff)

    def test_admin_lists_and_filters_expected_fields(self):
        model_admin = CustomUserAdmin(CustomUser, admin.site)

        self.assertEqual(
            model_admin.get_list_display(None),
            ("email", "role", "is_verified", "is_active"),
        )
        self.assertEqual(
            model_admin.get_list_filter(None),
            ("role", "is_verified"),
        )
        self.assertEqual(
            model_admin.get_search_fields(None),
            ("email", "username"),
        )

    def test_admin_add_form_exposes_email_and_username(self):
        self.assertEqual(
            CustomUserAdmin.add_form.base_fields.keys(),
            {"email", "username", "password1", "password2"},
        )
