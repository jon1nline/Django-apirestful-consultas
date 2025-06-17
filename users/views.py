from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from .serializers import UserSerializer, LoginSerializer
from .models import User
from datetime import datetime, timezone, timedelta
import jwt


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
            
        payload = {
            'id': user.id,
            'exp': datetime.now(timezone.utc) + timedelta(minutes=60),
            'iat': datetime.now(timezone.utc)
        }    

        token = jwt.encode(payload, 'chave_secreta', algorithm='HS256')
        
        response = Response()

        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt': token
        }
        return response 
        
class UserView(APIView):

    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('O usuário precisa entrar na conta')
        try:
            payload = jwt.decode(token,'chave_secreta',algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('O usuário precisa entrar na conta')
        
        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)

        return Response(serializer.data)