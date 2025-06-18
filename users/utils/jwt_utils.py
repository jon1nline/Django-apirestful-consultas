import jwt
from datetime import datetime, timedelta, timezone
from django.conf import settings
from django.http import JsonResponse
from users.models import User


def criar_token(user):
   
    # Payload para o token de acesso
    access_payload = {
        'id': user.id,
        'token_type': 'access',
        'exp': datetime.now(timezone.utc) + timedelta(minutes=60), 
        'iat': datetime.now(timezone.utc)
    }

    # Payload para o token de refresh 
    refresh_payload = {
        'id': user.id,
        'token_type': 'refresh',
        'exp': datetime.now(timezone.utc) + timedelta(days=7),
        'iat': datetime.now(timezone.utc)
    }

    # Gera o access token 
    access_token = jwt.encode(
        access_payload,
        settings.SECRET_KEY,
        algorithm='HS256'
    )
    
    # Gera o refresh token u
    refresh_token = jwt.encode(
        refresh_payload,
        settings.SECRET_KEY + user.password, #usa a senha, senha alterada = token invalidado
        algorithm='HS256'
    )

    return {
        'access': access_token,
        'refresh': refresh_token
    }

def verificar_token_cookies(request):
    
    access_token = request.COOKIES.get('access_token')

    if not access_token:
        return None, JsonResponse({'error': 'Token de acesso não encontrado.'}, status=401)

    try:
        # 1. Tenta decodificar o access token com a chave secreta principal
        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=['HS256'])
        user = User.objects.get(id=payload['id'])
        return user, None  

    except User.DoesNotExist:
        return None, JsonResponse({'error': 'Usuário associado ao token não encontrado.'}, status=401)

    except jwt.ExpiredSignatureError:
        # 2. Se o access token expirou, tenta usar o refresh token.
        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            return None, JsonResponse({'error': 'Sessão expirada. Faça login novamente.'}, status=401)

        try:
            #  Decodifica o payload do refresh token SEM verificar a assinatura para obter o 'id' do usuário.
            #  Isso é necessário para buscar o usuário e sua senha para construir a chave secreta correta.
            unverified_payload = jwt.decode(refresh_token, options={"verify_signature": False})
            
            if unverified_payload.get('token_type') != 'refresh':
                return None, JsonResponse({'error': 'Tipo de token inválido'}, status=401)

            # Busca o usuário no banco de dados.
            user = User.objects.get(id=unverified_payload['id']) 

            # AGORA, constrói a chave secreta correta e verifica a assinatura do refresh token.
            jwt.decode(
                refresh_token,
                settings.SECRET_KEY + user.password, 
                algorithms=['HS256']
            )

            #gera os novos tokens
            new_tokens = criar_token(user)

            response = JsonResponse({'message': 'Tokens renovados com sucesso.'})
            response.set_cookie(
                key='access_token',
                value=new_tokens['access'],
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax'
            )
            response.set_cookie(
                key='refresh_token',
                value=new_tokens['refresh'],
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax'
            )
            return user, response

        except jwt.ExpiredSignatureError:
            return None, JsonResponse({'error': 'Sessão expirada. Faça login novamente.'}, status=401)
        
        except (jwt.DecodeError, jwt.InvalidTokenError, User.DoesNotExist):
            return None, JsonResponse({'error': 'Não foi possível validar a sessão.'}, status=401)

    except jwt.InvalidTokenError:
        return None, JsonResponse({'error': 'Token de acesso inválido.'}, status=401)