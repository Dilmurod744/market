from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.admin.admin import BaseUserAdmin
from apps.models import User
from apps.proxies import OperatorProxy, AdminProxy, CurrierProxy, ManageerProxy


@admin.register(AdminProxy)
class AdminProxyModelAdmin(BaseUserAdmin):
    list_display = ['username']

    def get_queryset(self, request):
        return super().get_queryset(request).filter(status=User.Type.ADMIN)


@admin.register(CurrierProxy)
class CurrierProxyModelAdmin(BaseUserAdmin):
    list_display = ['username']

    def get_queryset(self, request):
        return super().get_queryset(request).filter(status=User.Type.CURRIER)


# @admin.register(UserProxy)
# class UserProxyModelAdmin(UserAdmin):
#     list_display = ['username']


@admin.register(OperatorProxy)
class OperatorProxyModelAdmin(BaseUserAdmin):
    list_display = ['username']

    def get_queryset(self, request):
        return super().get_queryset(request).filter(status=User.Type.OPERATOR)


@admin.register(ManageerProxy)
class ManageerProxyModelAdmin(BaseUserAdmin):
    list_display = ['username']

    def get_queryset(self, request):
        return super().get_queryset(request).filter(status=User.Type.MANAGER)
