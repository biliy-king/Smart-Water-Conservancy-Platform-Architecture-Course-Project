from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'data', views.MonitorDataViewSet, basename='monitordata')

urlpatterns = [
    path('', include(router.urls)),
    
    # 虚拟实时接口
    path('latest/', views.get_latest_data, name='latest-all'),
    path('latest/<int:point_id>/', views.get_latest_data, name='latest-detail'),
    path('history/<int:point_id>/', views.get_history_data, name='history'),
    path('alerts/', views.get_alert_summary, name='alerts'),
    path('statistics/', views.statistics_view, name='statistics'),  # GET /api/monitoring/statistics/
    
    # 健康检查
    path('health/', views.health_check, name='health'),
]