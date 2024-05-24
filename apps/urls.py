from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from apps.views import ProductListView, ProductDetailView, \
    UserTemplateView, WishlistView, OrderFormView, UserUpdateView, \
    ChangePasswordView, OrderedDetailView, WishlistPageView, DeleteWishlistView, \
    MarketAllListView, ThreadFormView, ThreadListView, NewOrderListView, \
    ReadyOrderListView, DeliveringOrderListView, WaitingOrderListView, ArchivedOrderListView, BrokenOrderListView, \
    DeliveredOrderListView, CancelledOrderListView, HoldOrderListView, AllOrderListView, \
    HolatUpdateView, StatisticListView, NewOrderCreateView, Currier, CompetitionListView, RequestsTemplateView, \
    PaymentTemplateView, LoginBotTemplateView, LoginCheckView, RegisterFormView, ForgotPasswordTemplateView, \
    ErrorPage404TemplateView, ErrorPage500TemplateView, MarketListView, OrderAcceptedUpdateView
from root import settings

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('product-detail/<str:slug>', ProductDetailView.as_view(), name='product_detail'),

    path('login', LoginView.as_view(template_name='apps/auth/login.html', redirect_authenticated_user=True,
                                    next_page='product_list'), name='login'),
    path('login-bot', LoginBotTemplateView.as_view(), name='login_bot'),
    path('logout', LogoutView.as_view(template_name='apps/auth/logout.html', next_page='login'), name='logout'),
    path('login-check', LoginCheckView.as_view(), name='login_check'),
    path('register', RegisterFormView.as_view(), name='register'),
    path('profile', UserTemplateView.as_view(), name='user_profile'),
    path('profile/update', UserUpdateView.as_view(), name='update'),
    path('forgot-password', ForgotPasswordTemplateView.as_view(), name='forgot_password'),
    path('change-password', ChangePasswordView.as_view(), name='change_password'),

    path('wishlist/<int:product_id>', WishlistView.as_view(), name='wishlist_create'),
    path('wishlist', WishlistPageView.as_view(), name='wishlists'),
    path('wishlist/delete/<int:pk>', DeleteWishlistView.as_view(), name='wishlists_delete'),

    path('order', OrderFormView.as_view(), name='order'),
    path('ordered/<int:pk>', OrderedDetailView.as_view(), name='ordered'),

    path('error-404', ErrorPage404TemplateView.as_view(), name='error_404'),
    path('error-500', ErrorPage500TemplateView.as_view(), name='error_500'),

    path('market/all', MarketAllListView.as_view(), name='market_all'),
    path('market', MarketListView.as_view(), name='market'),

    path('thread', ThreadFormView.as_view(), name='threads'),
    path('thread-list', ThreadListView.as_view(), name='thread_list'),
    path('thread-list/<int:pk>', ProductDetailView.as_view(), name='thread_list'),

]

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
    path('operator/order/<int:pk>', OrderAcceptedUpdateView.as_view(), name='order_accepted'),
    path('operator/holat/<int:pk>', HolatUpdateView.as_view(), name='holat_update'),
    path('operator/currier', Currier.as_view(), name='currier'),
    path('operator/product-add', NewOrderCreateView.as_view(), name='product-add'),

    path('statistics', StatisticListView.as_view(), name='statistics'),
    path('competition', CompetitionListView.as_view(), name='competition'),
    path('requests', RequestsTemplateView.as_view(), name='requests'),
    path('payment', PaymentTemplateView.as_view(), name='payments'),

]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL,
                                                                                        document_root=settings.MEDIA_ROOT)
