from datetime import datetime

from django.template import Library

from apps.models import WishList

register = Library()


@register.filter()
def custom_slice(value, arg):
    a, b = map(int, arg.split(':'))
    return list(value)[a:b]


@register.filter()
def has_wishlist(user_id, product_id):
    return WishList.objects.filter(user_id=user_id, product_id=product_id).exists()


# @register.filter(name='format_date')
# def format_date(date_string):
#     return datetime.strptime(date_string, "d-B, Y-yil H:i")
