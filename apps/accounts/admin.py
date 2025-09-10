from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
	"""Admin configuration for custom User model."""
	model = User
	list_display = ("id", "email", "username", "first_name", "last_name", "is_staff", "is_active", "date_joined")
	list_filter = ("is_staff", "is_active", "is_superuser")
	search_fields = ("email", "username", "first_name", "last_name")
	ordering = ("-date_joined",)

	fieldsets = (
		(None, {"fields": ("email", "username", "password")}),
		("Personal info", {"fields": ("first_name", "last_name", "avatar", "bio")} ),
		("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")} ),
		("Important dates", {"fields": ("last_login", "date_joined")} ),
	)

	add_fieldsets = (
		(None, {
			"classes": ("wide",),
			"fields": ("email", "username", "password", "password_confirm", "is_staff", "is_active")
		}),
	)

