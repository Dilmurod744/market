from django.conf.urls.static import static
from django.contrib.auth.views import LoginView
from django.urls import path

from apps.views import ProductListView, ProductDetailView, LogoutView, RegisterView, ForgotPasswordView, \
    UserTemplateView, WishlistView, OrderFormView, ErrorPage404View, ErrorPage500View, UserUpdateView, \
    ChangePasswordView, OrderedDetailView, WishlistPageView, DeleteWishlistView, OperatorView, MarketView, \
    MarketAllListView, ThreadListView, ThreadFormView, StatisticsListView, ThreadListView
from root import settings

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('product-detail/<str:slug>', ProductDetailView.as_view(), name='product_detail'),
    path('login', LoginView.as_view(template_name='apps/auth/login.html', next_page='product_list'), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('register', RegisterView.as_view(), name='register'),
    path('forgot_password', ForgotPasswordView.as_view(), name='forgot_password'),
    path('profile', UserTemplateView.as_view(), name='user_profile'),
    path('wishlist/<int:product_id>', WishlistView.as_view(), name='wishlist_create'),
    path('order', OrderFormView.as_view(), name='order'),
    path('ordered/<int:pk>', OrderedDetailView.as_view(), name='ordered'),
    path('profile/update', UserUpdateView.as_view(), name='update'),
    path('change_password', ChangePasswordView.as_view(), name='change_password'),
    path('error_404', ErrorPage404View.as_view(), name='error_404'),
    path('error_500', ErrorPage500View.as_view(), name='error_500'),
    path('wishlist', WishlistPageView.as_view(), name='wishlists'),
    path('wishlist/delete/<int:pk>', DeleteWishlistView.as_view(), name='wishlists_delete'),
    path('operator', OperatorView.as_view(), name='operator'),
    path('market/all', MarketAllListView.as_view(), name='market_all'),
    path('market', MarketView.as_view(), name='market'),
    path('thread', ThreadFormView.as_view(), name='threads'),
    path('thread_list', ThreadListView.as_view(), name='thread_list'),
    path('statistics', StatisticsListView.as_view(), name='statistics')
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL,
                                                                                        document_root=settings.MEDIA_ROOT)
