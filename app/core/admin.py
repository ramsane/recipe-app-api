from django.contrib import admin
# import default user admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# import our models from core app
from core import models

from django.utils.translation import gettext as _


class UserAdmin(BaseUserAdmin):
    # display the list withh email and name ordered by it's id
    ordering = ['id']
    list_display = ['email', 'name']
    # filed sets : Fields that we want to get displayed in admin page
    fieldsets = (
        (None, {
            "fields": ('email', 'password'),
        }),
        (_("Personal Info"), {
            "fields": ('name',)
        }),
        (_("Permissions"), {
            "fields": ('is_active', 'is_staff', 'is_superuser')
        }),
        (_("Important dates"), {
            "fields": ('last_login',)
        })
    )
    add_fieldsets = (
        (None, {
            'classes':('wide',),
            'fields':('email', 'password1', 'password2')
        }),
    )


# register our custom user to the admin app
admin.site.register(models.User, UserAdmin)

