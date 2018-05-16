from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from rest_framework.exceptions import ValidationError

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken

from exceptions.exceptions import INVALID_CREDENTIALS_ERROR
from exceptions.serializers import ErrorMessageSerializer


class LoginView(ObtainAuthToken):

    @csrf_exempt
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            return ObtainAuthToken.post(self, request, *args, **kwargs)
        except ValidationError:
            return Response(ErrorMessageSerializer(INVALID_CREDENTIALS_ERROR).data, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):

    permission_classes = (IsAuthenticated,)

    @csrf_exempt
    @transaction.atomic
    def post(self, request):
        request.user.auth_token.delete()
        return Response({}, status=status.HTTP_200_OK)
