from rest_framework.routers import DefaultRouter
from .views import EmployeeDocumentViewSet

router = DefaultRouter()
router.register('', EmployeeDocumentViewSet, basename='document')

urlpatterns = router.urls
