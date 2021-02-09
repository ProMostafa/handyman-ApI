from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from .views import ServiceViewSet, SubServicesViewSet, CustomerOrder,\
    ProductView, ReportService, RateTechnicianJob, ClientsReview, LatestBlogs
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('services', ServiceViewSet)
router.register('subservices', SubServicesViewSet)
router.register('customerorders', CustomerOrder)
router.register('products', ProductView)
urlpatterns = [
    path('', include(router.urls)),
    path('report/', ReportService.as_view(),name='report'),
    path('rate/', RateTechnicianJob.as_view(),name='rate'),
    path('get_reviews/', ClientsReview.as_view(),name='get_reviews'),
    path('get_news/', LatestBlogs.as_view(),name='get_news')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)