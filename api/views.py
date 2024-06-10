from rest_framework import generics, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer

class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

class LoginView(generics.GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        user = User.objects.filter(email=email).first()

        if user is not None and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

class UserPagination(PageNumberPagination):
    page_size = 10

class UserSearchView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = UserPagination

    def get_queryset(self):
        keyword = self.request.query_params.get('search', '').strip()
        if '@' in keyword:
            # Exact match on email
            return User.objects.filter(email__iexact=keyword)
        else:
            # Partial match on name
            return User.objects.filter(name__icontains=keyword)
