from django.contrib import admin
from .models import Classroom, ClassroomStudent

admin.site.register(Classroom)
admin.site.register(ClassroomStudent)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'role', 'is_active_student')
    fieldsets = UserAdmin.fieldsets + (
        ('Role Info', {'fields': ('role', 'is_active_student')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role Info', {'fields': ('role', 'is_active_student')}),
    )


admin.site.register(CustomUser, CustomUserAdmin)