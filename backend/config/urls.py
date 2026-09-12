from django.contrib import admin
from django.urls import include, path
from documents.views import DocumentViewSet
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()

router.register(
    "documents",
    DocumentViewSet,
    basename="document",
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "api/auth/token/",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path(
        "api/auth/token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path(
        "api/auth/",
        include("accounts.urls"),
    ),
    path(
        "api/",
        include(router.urls),
    ),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
