"""Flex Travels Activity URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.urls import path
from django.conf.urls import url, include

# Django Admin
from django.contrib import admin

# REST Framework
from rest_framework import routers
from rest_framework import permissions

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from entry import settings

# Modules
from dictionary.views import DictionaryViewSet
from common.views import UserProfileViewSet, GroupViewSet, home_page, PermissionViewSet, UserViewSet

schema_view = get_schema_view(
    openapi.Info(
        title="Flex Travels API",
        default_version='v1',
        description="Document for Flex Travels API",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="admin@cycling-cap.cn"),
        license=openapi.License(name="BSD License"),
    ),
    public=False,
    permission_classes=(permissions.IsAuthenticated,),
)

router = routers.DefaultRouter()
router.register(r'dictionaries', DictionaryViewSet)
router.register(r'users', UserProfileViewSet)
router.register(r'auth/users', UserViewSet)
router.register(r'groups', GroupViewSet)


urlpatterns = [
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('admin/', admin.site.urls),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^$', home_page),
    url('api/', include(router.urls)),
    url(r'^api/token/auth', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    url(r'^api/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    url(r'^api/token/verify', TokenVerifyView.as_view(), name='token_verify'),
    url(r'^api/auth', include('rest_framework.urls', namespace='rest_framework')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + \
               static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
