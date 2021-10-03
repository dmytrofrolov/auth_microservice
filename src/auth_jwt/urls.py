from rest_framework_jwt.views import obtain_jwt_token, verify_jwt_token
from django.urls import path
from .views import CreateUserView, TestSecuredView, manage_user

urlpatterns = [
    path('register/', CreateUserView.as_view({'post': 'create'}), name='register_user'),
    path('login/', obtain_jwt_token, name='login_user'),
    path('user/', manage_user, name='manage_user'),
    path('secure/', TestSecuredView.as_view(), name='secure_endpoint'),
    path('token_verify/', verify_jwt_token, name='verify_jwt_token'),
]
