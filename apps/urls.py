from django.conf.urls.static import static
from django.contrib.auth.views import LoginView
from django.urls import path

from apps.views import ProductListView, ProductDetailView, LogoutView, RegisterView, ForgotPasswordView, \
    UserTemplateView, WishlistView, OrderFormView, ErrorPage404View, ErrorPage500View, UserUpdateView, \
    ChangePasswordView, OrderedDetailView, WishlistPageView, DeleteWishlistView, MarketView, \
    MarketAllListView, ThreadFormView, ThreadListView, NewOrderListView, \
    ReadyOrderListView, DeliveringOrderListView, WaitingOrderListView, ArchivedOrderListView, BrokenOrderListView, \
    DeliveredOrderListView, CancelledOrderListView, HoldOrderListView, AllOrderListView, OrderAcceptedView, \
    HolatUpdateView, StatisticListView, NewOrderCreateView, Currier
from root import settings

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('product-detail/<str:slug>', ProductDetailView.as_view(), name='product_detail'),
    path('thread_list/<int:pk>', ProductDetailView.as_view(), name='thread_list'),
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
    # path('operator', OperatorView.as_view(), name='operator'),
    path('market/all', MarketAllListView.as_view(), name='market_all'),
    path('market', MarketView.as_view(), name='market'),
    path('thread', ThreadFormView.as_view(), name='threads'),
    path('thread_list', ThreadListView.as_view(), name='thread_list'),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL,
                                                                                        document_root=settings.MEDIA_ROOT)

urlpatterns += [
    path('operator/new', NewOrderListView.as_view(), name='new'),
    path('operator/ready', ReadyOrderListView.as_view(), name='ready'),
    path('operator/delivering', DeliveringOrderListView.as_view(), name='delivering'),
    path('operator/waiting', WaitingOrderListView.as_view(), name='waiting'),
    path('operator/archived', ArchivedOrderListView.as_view(), name='archived'),
    path('operator/broken', BrokenOrderListView.as_view(), name='broken'),
    path('operator/delivered', DeliveredOrderListView.as_view(), name='delivered'),
    path('operator/cancelled', CancelledOrderListView.as_view(), name='cancelled'),
    path('operator/hold', HoldOrderListView.as_view(), name='hold'),
    path('operator/all', AllOrderListView.as_view(), name='all'),
    path('operator/order/<int:pk>', OrderAcceptedView.as_view(), name='order_accepted'),
    path('operator/holat/<int:pk>', HolatUpdateView.as_view(), name='holat_update'),

    path('statistics', StatisticListView.as_view(), name='statistics'),
    path('product-add', NewOrderCreateView.as_view(), name='product-add'),
    path('operator/currier', Currier.as_view(), name='currier'),

]
