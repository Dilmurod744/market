from datetime import timedelta

from ckeditor.fields import RichTextField
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, IntegerField, PositiveIntegerField, TextChoices, ForeignKey, JSONField, \
    BooleanField, TextField, Model, CASCADE, DateTimeField, SlugField, TimeField, DateField
from django.db.models import SET_NULL, DecimalField
from django.utils.text import slugify
from django.utils.timezone import now
from django_resized import ResizedImageField
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from apps.tasks import send_new_product_notification


class BaseModel(Model):
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    def created_at_product(self):
        return self.created_at.strftime("%d.%m.%Y")

    class Meta:
        abstract = True


class UserManager(BaseUserManager):

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, email, password, **extra_fields)


class User(AbstractUser):
    class Type(TextChoices):
        ADMIN = "admin", "Admin"
        CURRIER = "currier", "Yetkazib beruvchi"
        USERS = "users", "Foydalanuvchi"
        OPERATOR = "operator", "Operator"
        MANAGER = "manager", "Menejer"

    # type = CharField(max_length=25, choices=Type.choices, default=Type.USERS)
    intro = TextField(max_length=1024, null=True, blank=True)
    avatar = ResizedImageField(size=[168, 168], upload_to='user_avatars/', null=True, blank=True,
                               default='user_avatars/avatar_default.jpeg')
    banner = ResizedImageField(size=[1198, 124], upload_to='user_banners/', null=True, blank=True,
                               default='user_avatars/banner_default.jpg')
    workout = CharField(max_length=50)
    country = CharField(max_length=30)
    is_verified = BooleanField(default=False)
    phone_number = CharField(max_length=25)
    status = CharField(max_length=25, choices=Type.choices, default=Type.USERS)
    from_working_time = TimeField(null=True, blank=True)  # verbose_name="...dan ishlash")
    to_working_time = TimeField(null=True, blank=True)  # verbose_name="...gacha ishlash")
    region = ForeignKey('apps.Region', CASCADE, null=True, blank=True)
    district = ForeignKey('apps.District', CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = 'Foydalanuvchi '
        verbose_name_plural = 'Foydalanuvchilar'


class Category(MPTTModel):
    name = CharField(max_length=25)
    slug = SlugField(max_length=25, null=True, blank=True, unique=True)
    parent = TreeForeignKey('self', SET_NULL, related_name='subcategory', null=True, blank=True)
    image = ResizedImageField(size=[100, 100], upload_to='category_images/', null=True, blank=True,
                              default='user_avatars/banner_default.jpg')

    class Meta:
        verbose_name = 'Kategoriya '
        verbose_name_plural = 'Kategoriyalar'

    def __str__(self):
        return self.name

    def _get_unique_slug(self):
        slug = slugify(self.name)
        unique_slug = slug
        num = 1
        while Product.objects.filter(slug=unique_slug).exists():
            unique_slug = f'{slug}-{num}'
            num += 1
        return unique_slug

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.slug = self._get_unique_slug()
        if force_update is True:
            self.slug = slugify(self.name)
        return super().save(force_insert, force_update, using, update_fields)


class Product(BaseModel):
    name = CharField(max_length=255)
    description = RichTextField()
    price = DecimalField(max_digits=9, decimal_places=2)
    discount = IntegerField(default=0)
    specifications = JSONField(null=True, blank=True)
    shipping = DecimalField(max_digits=9, decimal_places=2)
    quantity = PositiveIntegerField(default=0)
    slug = SlugField(max_length=255, null=True, blank=True, unique=True)
    payment_for_operator = DecimalField(max_digits=9, decimal_places=2)
    category = ForeignKey('apps.Category', CASCADE, 'categories')

    class Meta:
        verbose_name = 'Mahsulot '
        verbose_name_plural = 'Mahsulotlar'

    def _get_unique_slug(self):
        slug = slugify(self.name)
        unique_slug = slug
        num = 1
        while Product.objects.filter(slug=unique_slug).exists():
            unique_slug = f'{slug}-{num}'
            num += 1
        return unique_slug

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.slug = self._get_unique_slug()
        if force_update is True:
            self.slug = slugify(self.name)
        return super().save(force_insert, force_update, using, update_fields)

    def save_1(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        users_emails = list(User.objects.values_list('email', flat=True))
        send_new_product_notification.delay(users_emails, self.name, 'https://www.youtube.com/', )

    def __str__(self):
        return self.name

    @property
    def stock(self):
        if self.quantity > 0:
            return "Sotuvda bor"
        else:
            return "Sotuvda yo`q"

    @property
    def is_new(self):
        return self.created_at >= now() - timedelta(days=7)

    @property
    def discount_price(self):
        return self.discount * self.price / 100

    @property
    def sell_price(self):
        return self.price - self.discount_price


class ProductImage(Model):
    image = ResizedImageField(size=[1098, 717], upload_to='product_images/', null=True, blank=True)
    product = ForeignKey('apps.Product', CASCADE, related_name='images')

    def __repr__(self):
        return self.product.name


class WishList(Model):
    user = ForeignKey('apps.User', CASCADE, related_name='wishlists')
    product = ForeignKey('apps.Product', CASCADE)
    added_at = DateTimeField(auto_now_add=True)


class Order(BaseModel):
    class Status(TextChoices):
        NEW = 'yangi', 'Yangi'
        ARCHIVE = 'arxivlandi', 'Arxivlandi'
        DELIVERING = 'yetkazilmoqda', 'Yetkazilmoqda'
        BROKEN = 'nosoz_mahsulot', 'Nosoz_mahsulot'
        DELIVERED = 'yetkazib_berildi', 'Yetkazib_berildi'
        RETURNED = 'qaytib_keldi', 'Qaytib_keldi'
        CANCELLED = 'bekor_qilindi', 'Bekor_qilindi'
        WAITING = 'keyin_oladi', 'Keyin_oladi'
        HOLD = 'hold', 'Hold'
        READY_TO_DELIVERY = 'dastavkaga_tayyor', 'Dastavkaga_tayyor'

    name = CharField(max_length=20)
    quantity = IntegerField(default=0)
    phone_number = CharField(max_length=20)
    status = CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    comment = CharField(max_length=512, null=True, blank=True)
    region = ForeignKey('apps.Region', SET_NULL, null=True, blank=True)
    district = ForeignKey('apps.District', SET_NULL, null=True, blank=True)
    product = ForeignKey('apps.Product', CASCADE)
    thread = ForeignKey('apps.Thread', SET_NULL, blank=True, null=True, related_name='orders')
    user = ForeignKey('apps.User', CASCADE, 'user', blank=True, null=True, verbose_name='Foydalanuvchi')


class SiteSettings(Model):
    delivery_price = DecimalField(max_digits=9, decimal_places=2, default=30_000)


class Region(Model):
    name = CharField(max_length=30)

    def __str__(self):
        return self.name


class District(Model):
    name = CharField(max_length=30)
    region = ForeignKey('apps.Region', CASCADE, related_name='districts')

    def __str__(self):
        return self.name


class Thread(BaseModel):
    name = CharField(max_length=35)
    counter = IntegerField(default=0)
    sale = DecimalField(max_digits=9, decimal_places=2, default=0, null=True)
    additional_benefits = DecimalField(max_digits=9, decimal_places=2, default=0, null=True)
    user = ForeignKey('apps.User', CASCADE, related_name='user_thread')
    product = ForeignKey('apps.Product', CASCADE, related_name='product_thread')


class Competition(Model):
    title = CharField(max_length=255)
    photo = ResizedImageField(size=[1220, 1220], upload_to='competition_images/', null=True, blank=True)
    start_date = DateField()
    end_date = DateField()
    is_active = BooleanField(default=True)

    class Meta:
        verbose_name = 'Konkurs '
        verbose_name_plural = 'Konkurslar'
