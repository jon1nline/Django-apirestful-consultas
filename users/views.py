from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from .serializers import UserSerializer, LoginSerializer
from .models import User
from datetime import datetime, timezone, timedelta
from .utils.jwt_utils import criar_token 
import jwt
from django.http import JsonResponse
from django.conf import settings


class RegistroUsuario(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class LoginUsuario(generics.CreateAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = authenticate(
            request,
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        
        if not user:
            return Response(
                {"detail": "e-mail ou senha invalidos"},
                status=status.HTTP_401_UNAUTHORIZED
            )
              

        token = criar_token(user)
        
        response = JsonResponse({'message': 'Usuário conectado.'})
            
            
        response.set_cookie(
                'access_token',
                token['access'],
                httponly=True,
                secure=False,      
                samesite='Lax',
               
            )
            
        response.set_cookie(
                'refresh_token',
                token['refresh'],
                httponly=True,
                secure=False,      
                samesite='Lax',
                max_age=604800  # dura 7 dias
            )

            
        return response
        
class UserView(APIView):

    def get(self, request):
        token = request.COOKIES.get('access_token')

        if not token:
            raise AuthenticationFailed('O usuário precisa entrar na conta')
        try:
            payload = jwt.decode(token,settings.SECRET_KEY,algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('O usuário precisa entrar na conta')
        
        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)
        
        return Response(serializer.data)