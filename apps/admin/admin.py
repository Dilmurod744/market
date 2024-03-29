from django import forms
from django.contrib import admin
from django.contrib.admin import StackedInline, ModelAdmin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe
from import_export.admin import ImportExportModelAdmin
from mptt.admin import DraggableMPTTAdmin

from apps.models import Product, Category, ProductImage, User, SiteSettings
from apps.resources import ProductModelResource


class CategoryModelForm(forms.ModelForm):
    class Meta:
        model = Category
        exclude = ()


@admin.register(Category)
class CategoryMPTTModelAdmin(DraggableMPTTAdmin):
    mptt_level_indent = 20
    form = CategoryModelForm


class ProductImageStackedInline(StackedInline):
    model = ProductImage
    min_num = 1
    extra = 0
    fields = ['image']


@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    def form_description(self, obj):
        return mark_safe(obj.description)

    inlines = (ProductImageStackedInline,)
    list_display = ['id', 'name', 'form_description', 'price', 'quantity', 'category', 'image_show',
                    'created_at_product']
    search_fields = ['id', 'name']
    list_per_page = 10
    list_max_show_all = 20
    resource_class = ProductModelResource

    def response_post_save_add(self, request, obj):
        result = super().response_post_save_add(request, obj)
        # url = request.build_absolute_uri(reverse('product_detail', kwargs={'pk': obj.pk}))
        # send_new_product_notification.delay(product_name=obj.name, url=url)
        return result

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super(ProductAdmin, self).get_queryset(request)

        #     return super(ProductAdmin, self).get_queryset(request)
        else:
            qs = super(ProductAdmin, self).get_queryset(request)
        return qs.filter(owner=request.user)

    def image_show(self, obj: Product):
        if obj.images.first():
            return mark_safe("<img src='{}' width='200' />".format(obj.images.first().image.url))

        return ''

    image_show.description = 'images'


@admin.register(User)
class BaseUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (('Personal info'),
         {'fields': ('first_name', 'last_name', 'email', 'avatar', 'workout', 'country', 'is_verified', 'banner')}),
        (('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'avatar',),
        }),
    )
    # inlines = (UserImageStackedInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)


@admin.register(SiteSettings)
class SiteSettingsAdmin(ModelAdmin):
    list_display = ['delivery_price']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.unregister(Group)
