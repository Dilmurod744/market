from datetime import timedelta

from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.core.cache import cache
from django.db.models import Count, Q, Sum
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, TemplateView, FormView, DetailView, UpdateView, CreateView

from apps.forms import UserRegistrationForm, OrderModelForm, UserSettingsForm, ThreadModelForm, OrderAcceptedModelForm, \
    OrderCreateModelForm
from apps.mixins import NotLoginRequiredMixins
from apps.models import Product, User, SiteSettings, Order, Category, ProductImage, WishList, Thread, Region, \
    Competition
from apps.tasks import send_to_email
from .models import District


class CategoryTemplateView(TemplateView):
    template_name = 'apps/base.html'


class ProductListView(ListView):
    paginate_by = 9
    queryset = Product.objects.order_by('-id')
    template_name = 'apps/product/product_grid.html'
    context_object_name = 'product_list'

    def get_queryset(self):
        category_id = self.request.GET.get('category', None)
        if category_id:
            return self.queryset.filter(category_id=category_id)
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(parent_id=None)
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'apps/product/product_detail.html'

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg)
        slug = self.kwargs.get(self.slug_url_kwarg)
        if pk:
            thread = get_object_or_404(Thread.objects.all(), pk=pk)
            thread.counter += 1
            thread.save()
            return thread.product
        return get_object_or_404(Product.objects.all(), slug=slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(parent_id=None)
        context['thread_id'] = self.kwargs.get(self.pk_url_kwarg, '')
        return context


class ProductImageTemplateView(TemplateView):
    model = ProductImage
    template_name = 'apps/product/product_detail.html'
    context_object_name = 'product_image'


class RegisterFormView(NotLoginRequiredMixins, FormView):
    form_class = UserRegistrationForm
    template_name = 'apps/auth/register.html'
    success_url = '/'

    def form_valid(self, form):
        form.save()
        send_to_email.delay([form.data.get('email')], form.data.get('first_name'))
        return super().form_valid(form)


class ForgotPasswordTemplateView(TemplateView):
    template_name = 'apps/auth/forgot_password.html'


class ProductResourceListView(ListView):
    pass


class UserTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'apps/auth/profile.html'


class WishlistView(View):

    def get(self, request, *args, **kwargs):
        product_id = kwargs.get('product_id')
        wishlist, created = WishList.objects.get_or_create(user=request.user, product_id=product_id)
        if not created:
            wishlist.delete()
        return redirect('/')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(parent_id=None)
        return context


class OrderFormView(FormView):
    form_class = OrderModelForm
    template_name = 'apps/product/product_detail.html'

    def form_valid(self, form):
        order = form.save()
        order.product.quantity -= order.quantity
        order.product.save()
        return redirect('ordered', order.id)


class OrderedDetailView(DetailView):
    template_name = 'apps/product/ordered.html'
    queryset = Order.objects.all()
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        site_settings = SiteSettings.objects.first()
        context['delivery_price'] = site_settings.delivery_price
        return context


class UserUpdateView(UpdateView):
    form_class = UserSettingsForm
    template_name = 'apps/auth/profile.html'
    success_url = reverse_lazy('login')

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['regions'] = Region.objects.all()
        if region_id := self.request.user.region:
            context['districts'] = District.objects.filter(region_id=region_id)
        return context

    def form_invalid(self, form):
        return super().form_invalid(form)


class ChangePasswordView(PasswordChangeView):
    form_class = PasswordChangeForm
    template_name = 'apps/auth/profile.html'
    success_url = reverse_lazy('login')

    def form_invalid(self, form):
        return super().form_invalid(form)


class WishlistPageView(ListView):
    model = WishList
    template_name = 'apps/auth/wishlist_page.html'
    context_object_name = 'wishlists'

    def get_queryset(self):
        return WishList.objects.filter(user=self.request.user)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['total_sum'] = sum(self.get_queryset().values_list('product__price', flat=True))
        return context


class DeleteWishlistView(View):

    def get(self, request, pk=None):
        WishList.objects.filter(user_id=self.request.user.id, product_id=pk).delete()
        return redirect('wishlists')


class OperatorListView(ListView):
    model = Order
    template_name = 'apps/admin/operators.html'
    context_object_name = 'operators'


class MarketListView(LoginRequiredMixin, ListView):
    paginate_by = 2
    queryset = Product.objects.order_by('-id')
    template_name = 'apps/admin/market.html'
    context_object_name = 'products'

    def get_queryset(self):
        category_id = self.request.GET.get('category', None)
        if category_id:
            return self.queryset.filter(category_id=category_id)
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(parent_id=None)
        context['delivery_price'] = SiteSettings.objects.first().delivery_price
        return context


class MarketAllListView(ListView):
    paginate_by = 3
    queryset = Product.objects.order_by('-id')
    template_name = 'apps/admin/market.html'
    context_object_name = 'products'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(parent_id=None)
        context['delivery_price'] = SiteSettings.objects.first().delivery_price
        return context


class ThreadFormView(FormView):
    template_name = 'apps/admin/market.html'
    form_class = ThreadModelForm

    def form_valid(self, form):
        stream = form.save(False)
        stream.user = self.request.user
        stream.save()
        return redirect('thread_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['threads'] = Thread.objects.all()
        return context

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class ThreadListView(ListView):
    model = Thread
    template_name = 'apps/admin/thread.html'
    context_object_name = 'threads'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(parent_id=None)
        return context

    def get_queryset(self):
        return Thread.objects.all().order_by('-id')


class NewOrderListView(ListView):
    queryset = Order.objects.filter(status=Order.Status.NEW).order_by('-id')
    paginate_by = 10
    template_name = 'apps/operators/new_order.html'
    context_object_name = 'orders'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['regions'] = Region.objects.all()
        context['districts'] = District.objects.all()
        context['categories'] = Category.objects.filter(parent_id=None)
        return context


class ReadyOrderListView(ListView):
    queryset = Order.objects.filter(status=Order.Status.READY_TO_DELIVERY)
    paginate_by = 10
    template_name = 'apps/operators/ready_for_delivery.html'
    context_object_name = 'read_for_deliveries'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['regions'] = Region.objects.all()
        context['districts'] = District.objects.all()
        return context


class DeliveringOrderListView(ListView):
    queryset = Order.objects.filter(status=Order.Status.DELIVERING)
    paginate_by = 10
    template_name = 'apps/operators/delivering.html'
    context_object_name = 'deliveries'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['regions'] = Region.objects.all()
        context['districts'] = District.objects.all()
        return context


class WaitingOrderListView(ListView):
    queryset = Order.objects.filter(status=Order.Status.WAITING)
    paginate_by = 10
    template_name = 'apps/operators/waiting.html'
    context_object_name = 'waiting'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['regions'] = Region.objects.all()
        context['districts'] = District.objects.all()
        return context


class ArchivedOrderListView(ListView):
    queryset = Order.objects.filter(status=Order.Status.ARCHIVE)
    paginate_by = 10
    template_name = 'apps/operators/archived.html'
    context_object_name = 'archived'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['regions'] = Region.objects.all()
        context['districts'] = District.objects.all()
        return context


class BrokenOrderListView(ListView):
    queryset = Order.objects.filter(status=Order.Status.BROKEN)
    paginate_by = 10
    template_name = 'apps/operators/broken.html'
    context_object_name = 'broken'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['regions'] = Region.objects.all()
        context['districts'] = District.objects.all()
        return context


class DeliveredOrderListView(ListView):
    queryset = Order.objects.filter(status=Order.Status.DELIVERED)
    paginate_by = 10
    template_name = 'apps/operators/delivered.html'
    context_object_name = 'delivered'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['regions'] = Region.objects.all()
        context['districts'] = District.objects.all()
        return context


class CancelledOrderListView(ListView):
    queryset = Order.objects.filter(status=Order.Status.CANCELLED)
    paginate_by = 10
    template_name = 'apps/operators/cancelled.html'
    context_object_name = 'cancelled'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['regions'] = Region.objects.all()
        context['districts'] = District.objects.all()
        return context


class HoldOrderListView(ListView):
    queryset = Order.objects.filter(status=Order.Status.HOLD)
    paginate_by = 10
    template_name = 'apps/operators/hold.html'
    context_object_name = 'hold'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['regions'] = Region.objects.all()
        context['districts'] = District.objects.all()
        return context


class AllOrderListView(ListView):
    queryset = Order.objects.all()
    paginate_by = 10
    template_name = 'apps/operators/all.html'
    context_object_name = 'all_orders'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['regions'] = Region.objects.all()
        context['districts'] = District.objects.all()
        return context


class OrderAcceptedUpdateView(UpdateView):
    model = Order
    form_class = OrderAcceptedModelForm
    template_name = 'apps/admin/accepted_order.html'
    success_url = reverse_lazy('new')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['regions'] = Region.objects.all()
        context['districts'] = District.objects.all()
        return context


class HolatUpdateView(UpdateView):
    model = Order
    form_class = OrderAcceptedModelForm
    template_name = 'apps/admin/holatni_ozgartirish.html'
    success_url = reverse_lazy('ready')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['regions'] = Region.objects.all()
        context['districts'] = District.objects.all()
        return context


class NewOrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderCreateModelForm
    template_name = 'apps/operators/zakaz.html'
    success_url = reverse_lazy('new')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['regions'] = Region.objects.all()
        return context


class StatisticListView(ListView):

    def get_queryset(self):
        period = self.request.GET.get('period', 'all')
        now = timezone.now()

        if period == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'last_day':
            start_date = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'weekly':
            start_date = (now - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'monthly':
            start_date = (now - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0)

        else:
            start_date = None

        queryset = Thread.objects.all()

        if start_date:
            queryset = queryset.filter(orders__created_at__gte=start_date)

        return queryset.annotate(
            new=Count('orders', filter=Q(orders__status=Order.Status.NEW)),
            archive=Count('orders', filter=Q(orders__status=Order.Status.ARCHIVE)),
            ready_to_delivery=Count('orders', filter=Q(orders__status=Order.Status.READY_TO_DELIVERY)),
            delivering=Count('orders', filter=Q(orders__status=Order.Status.DELIVERING)),
            delivered=Count('orders', filter=Q(orders__status=Order.Status.DELIVERED)),
            waiting=Count('orders', filter=Q(orders__status=Order.Status.WAITING)),
            cancelled=Count('orders', filter=Q(orders__status=Order.Status.CANCELLED))
        ).select_related('product').all()

    template_name = 'apps/admin/statistics.html'
    context_object_name = 'statistics'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['categories'] = Category.objects.filter(parent_id=None)
        queryset = self.get_queryset()
        context.update(**queryset.aggregate(
            visit_total=Sum('counter'),
            new_total=Sum('new'),
            archived_total=Sum('archive'),
            ready_to_delivery_total=Sum('ready_to_delivery'),
            delivered_total=Sum('delivered'),
            delivering_total=Sum('delivering'),
            waiting_total=Sum('waiting'),
            cancelled_total=Sum('cancelled'),
        ))
        return context


class Currier(ListView):
    queryset = User.objects.filter(status=User.Type.CURRIER)
    context_object_name = 'couriers'
    template_name = 'apps/operators/currier.html'


class RequestsTemplateView(TemplateView):
    template_name = 'apps/admin/requests.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(parent_id=None)
        return context


class PaymentTemplateView(TemplateView):
    template_name = 'apps/admin/payment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(parent_id=None)
        return context


class LoginBotTemplateView(TemplateView):
    template_name = 'apps/auth/login_with_telegram_bot.html'


class LoginCheckView(View):
    def post(self, request, *args, **kwargs):
        code = request.POST.get('code', '')
        if len(code) != 6:
            return JsonResponse({'msg': 'error code'}, status=400)
        phone = cache.get(code)
        if phone is None:
            return JsonResponse({'msg': 'expired code'}, status=400)
        return JsonResponse({'msg': 'ok'}, status=200)


class MarketTopProductListView(ListView):
    model = Product
    paginate_by = 3
    context_object_name = 'products'
    template_name = 'apps/admin/market.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(parent_id=None)
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        category_slug = self.request.GET.get('category')
        if category_slug == 'market/top_products':
            queryset = self.get_top_products()
        elif category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        return queryset

    def get_top_products(self):
        today = timezone.now()
        last_week = today - timedelta(days=7)
        qs = Order.objects.filter(created_at__gte=last_week, status=Order.Status.DELIVERED)
        top_products = qs.values('product__id').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:5]
        product_ids = [item['product__id'] for item in top_products]
        return Product.objects.filter(id__in=product_ids)


class AdminPageTemplateView(TemplateView):
    template_name = 'apps/admin/admin_main_page.html'


class CompetitionTemplateView(TemplateView):
    template_name = 'apps/admin/konkurs.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(parent_id=None)
        context['competition'] = Competition.objects.filter(is_active=True).first()
        return context


def get_districts_by_region(request, region_id):
    districts = District.objects.filter(region_id=region_id).values('id', 'name')
    return JsonResponse(list(districts), safe=False)
