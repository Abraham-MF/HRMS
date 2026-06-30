from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet, DepartmentViewSet, JobPositionViewSet

router = DefaultRouter()
router.register('',           EmployeeViewSet,    basename='employee')
router.register('departments', DepartmentViewSet, basename='department')
router.register('positions',  JobPositionViewSet, basename='jobposition')

urlpatterns = router.urls