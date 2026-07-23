from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.views import RegisterView
from marketplace.views import CategoryViewSet, FavouriteViewSet, ListingViewSet, MessageViewSet
from payments.views import InitiatePaymentView, PesapalCallbackView, PesapalRedirectView, PaymentStatusView

router = DefaultRouter()
router.register("listings", ListingViewSet, basename="listing")
router.register("categories", CategoryViewSet, basename="category")
router.register("favorites", FavouriteViewSet, basename="favorite")
router.register("messages", MessageViewSet, basename="message")

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/accounts/register/", RegisterView.as_view(), name="register"),
    path("api/accounts/login/", TokenObtainPairView.as_view(), name="login"),
    path("api/accounts/login/refresh/", TokenRefreshView.as_view(), name="login-refresh"),

    path("api/payments/pay/", InitiatePaymentView.as_view(), name="initiate-payment"),
    path("api/payments/callback/", PesapalCallbackView.as_view(), name="pesapal-callback"),
    path("api/payments/redirect/", PesapalRedirectView.as_view(), name="pesapal-redirect"),
    path("api/payments/status/<int:transaction_id>/", PaymentStatusView.as_view(), name="payment-status"),

    path("api/", include(router.urls)),

    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)