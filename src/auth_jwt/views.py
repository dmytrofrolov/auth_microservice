from django.contrib.auth import get_user_model
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.settings import api_settings
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.views import APIView
from .serializers import RegisterUserSerializer, UpdateUserSerializer

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class CreateUserView(mixins.CreateModelMixin, GenericViewSet):
    """Registration view, creates user with password and saves it to database"""
    queryset = get_user_model().objects.all()
    serializer_class = RegisterUserSerializer

    def create(self, request, *args, **kwargs):
        response = super(CreateUserView, self).create(request, args, kwargs)
        payload = jwt_payload_handler(response.data.serializer.instance)
        token = jwt_encode_handler(payload)
        return Response({'token': token})


class ManageUserView(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, GenericViewSet):
    """CRUD endpoint for user to get/update/delete himself"""
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)
    queryset = get_user_model().objects.all()
    serializer_class = UpdateUserSerializer

    def get_object(self):
        return self.request.user


manage_user = ManageUserView.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})


class TestSecuredView(APIView):
    """Test view to verify authorization token works"""
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def get(self, request, format=None):
        return Response({'ok': True})
