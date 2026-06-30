from rest_framework.routers import DefaultRouter
from .views import (
    AttendanceViewSet, LeaveRequestViewSet,
    LeaveBalanceViewSet, LicenseViewSet,
)

router = DefaultRouter()
router.register('records',   AttendanceViewSet,   basename='attendance')
router.register('leaves',    LeaveRequestViewSet, basename='leave')
router.register('balances',  LeaveBalanceViewSet, basename='leave-balance')
router.register('licenses',  LicenseViewSet,      basename='license')

urlpatterns = router.urls
