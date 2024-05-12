from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.db.models import Count, Q, Sum
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, TemplateView, FormView, DetailView, UpdateView, CreateView

from apps.forms import UserRegistrationForm, OrderModelForm, UserSettingsForm, ThreadModelForm, OrderAcceptedModelForm, \
    OrderCreateModelForm
from apps.mixins import NotLoginRequiredMixins
from apps.models import Product, User, SiteSettings, Order, Category, ProductImage, WishList, Thread, Region
from apps.tasks import send_to_email
from django.http import JsonResponse
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


class ProductImageView(TemplateView):
    model = ProductImage
    template_name = 'apps/product/product_detail.html'
    context_object_name = 'product_image'


class LogoutView(ListView):
    model = User
    template_name = 'apps/auth/logout.html'
    context_object_name = 'logout'


class RegisterView(NotLoginRequiredMixins, FormView):
    form_class = UserRegistrationForm
    template_name = 'apps/auth/register.html'
    success_url = '/'

    def form_valid(self, form):
        form.save()
        send_to_email.delay([form.data.get('email')], form.data.get('first_name'))
        return super().form_valid(form)


class ForgotPasswordView(TemplateView):
    template_name = 'apps/auth/forgot_password.html'


class ProductResourceView(ListView):
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


class ErrorPage404View(TemplateView):
    template_name = 'apps/errors/error_404.html'


class ErrorPage500View(TemplateView):
    template_name = 'apps/errors/error_500.html'


class UserUpdateView(UpdateView):
    form_class = UserSettingsForm
    template_name = 'apps/auth/profile.html'
    success_url = reverse_lazy('login')

    def get_object(self, queryset=None):
        return self.request.user

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


class OperatorView(ListView):
    model = Order
    template_name = 'apps/admin/operators.html'
    context_object_name = 'operators'


class MarketView(LoginRequiredMixin, ListView):
    paginate_by = 9
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
    paginate_by = 9
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


class NewOrderListView(ListView):
    queryset = Order.objects.filter(status=Order.Status.NEW)
    paginate_by = 10
    template_name = 'apps/operators/new_order.html'
    context_object_name = 'orders'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['regions'] = Region.objects.all()
        context['districts'] = District.objects.all()
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


class OrderAcceptedView(UpdateView):
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
    queryset = Thread.objects.annotate(
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
