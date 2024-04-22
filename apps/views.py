from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, TemplateView, FormView, DetailView, UpdateView

from apps.forms import UserRegistrationForm, OrderModelForm, UserSettingsForm, ThreadModelForm
from apps.mixins import NotLoginRequiredMixins
from apps.models import Product, User, SiteSettings, Order, Category, ProductImage, WishList, Thread
from apps.tasks import send_to_email


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(parent_id=None)
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


class ThreadListView(ListView):
    queryset = Thread.objects.all()
    template_name = 'apps/admin/oqim.html'
    context_object_name = 'oqim'


class ThreadFormView(FormView):
    template_name = 'apps/admin/market.html'
    form_class = ThreadModelForm
    success_url = reverse_lazy('oqim')

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
    template_name = 'apps/admin/oqim.html'
    context_object_name = 'threads'


class StatisticsListView(ListView):
    queryset = Product.objects.all()
    template_name = 'apps/admin/statistics.html'
