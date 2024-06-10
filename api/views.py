from rest_framework import generics, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import FriendRequest, User
from .serializers import FriendRequestSerializer, UserSerializer

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

# Friend Request 
class SendFriendRequestView(APIView):
    def post(self, request, format=None):
        sender_email = request.user.email
        receiver_email = request.data.get('receiver')
        
        # Prevent users from sending friend requests to themselves
        if sender_email == receiver_email:
            return Response({'detail': 'You cannot send a friend request to yourself'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if a friend request already exists between the sender and receiver
        existing_request = FriendRequest.objects.filter(sender__email=sender_email, receiver__email=receiver_email).exists()
        if existing_request:
            return Response({'detail': 'Friend request already sent'}, status=status.HTTP_400_BAD_REQUEST)
        
        request.data['sender'] = sender_email
        request.data['status'] = 'pending'  # Set the status to 'pending'
        
        serializer = FriendRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class RespondFriendRequestView(APIView):
    def put(self, request, friend_request_id, format=None):
        friend_request = FriendRequest.objects.get(pk=friend_request_id)
        if friend_request.receiver.email == request.user.email:
            friend_request.status = request.data.get('status', friend_request.status)
            if friend_request.status == 'accepted':
                # Update the status to 'accepted' if the request is accepted
                friend_request.save()
                return Response({'detail': 'Friend request accepted'}, status=status.HTTP_200_OK)
            elif friend_request.status == 'rejected':
                # Update the status to 'rejected' if the request is rejected
                friend_request.delete()
                return Response({'detail': 'Friend request rejected'}, status=status.HTTP_200_OK)
        return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
class ListFriendsView(ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.friends.all()

class ListPendingRequestsView(ListAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FriendRequest.objects.filter(receiver=self.request.user, status=FriendRequest.PENDING)