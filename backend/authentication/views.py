from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user
    """
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        # Automatically log in the user after registration
        login(request, user)
        request.session.save()
        request.session.modified = True
        
        response = Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )
        
        # Explicitly set session cookie in response
        response.set_cookie(
            key='sessionid',
            value=request.session.session_key,
            max_age=86400,
            httponly=False,
            samesite='Lax',
            secure=False,
            path='/'
        )
        
        return response
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Login user
    """
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Ensure session is saved and cookie is set
            request.session.save()
            request.session.modified = True
            
            response = Response(
                UserSerializer(user).data,
                status=status.HTTP_200_OK
            )
            
            # Explicitly set session cookie in response
            response.set_cookie(
                key='sessionid',
                value=request.session.session_key,
                max_age=86400,
                httponly=False,
                samesite='Lax',
                secure=False,
                path='/'
            )
            
            return response
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Logout user
    """
    logout(request)
    return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """
    Get current user info
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_csrf_token(request):
    """
    Get CSRF token
    """
    from django.middleware.csrf import get_token
    return Response({'csrfToken': get_token(request)})
