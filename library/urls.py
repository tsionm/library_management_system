from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, UserViewSet
# from .views import BookViewSet, UserViewSet, TransactionViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView  # Import token views
from .views import BookViewSet, UserViewSet
# from .views import BookViewSet, UserViewSet, TransactionViewSet

router = DefaultRouter()
router.register(r'books', BookViewSet)
router.register(r'users', UserViewSet)
# router.register(r'transactions', TransactionViewSet)


urlpatterns = [
    path('', include(router.urls)),  # Include the router URLs
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Adjusted path
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Adjusted path
]


# The API URLs are now determined automatically by the router.
# urlpatterns = router.urls
