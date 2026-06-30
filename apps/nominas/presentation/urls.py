from rest_framework.routers import DefaultRouter
from .views import PayrollPeriodViewSet, PayrollRecordViewSet

router = DefaultRouter()
router.register('periods', PayrollPeriodViewSet, basename='payroll-period')
router.register('records', PayrollRecordViewSet, basename='payroll-record')

urlpatterns = router.urls
