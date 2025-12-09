from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, UpdateRSVPView, CreateReviewView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'events', EventViewSet, basename='events')

urlpatterns = [
    path('', include(router.urls)),
    path('events/<int:event_id>/rsvp/<int:user_id>/', UpdateRSVPView.as_view(), name='update-rsvp'),
    path('events/<int:event_id>/reviews/', CreateReviewView.as_view(), name='create-review'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
