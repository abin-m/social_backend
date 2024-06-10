from django.urls import path
from .views import ListFriendsView, ListPendingRequestsView,  RespondFriendRequestView, SendFriendRequestView, SignupView, LoginView, UserSearchView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('search/', UserSearchView.as_view(), name='user-search'),
    path('send-request/', SendFriendRequestView.as_view(), name='send_friend_request'),
    path('respond-request/<int:pk>/',  RespondFriendRequestView.as_view(), name='respond_to_friend_request'),
    path('list-friends/', ListFriendsView.as_view(), name='list_friends'),
    path('list-pending-requests/', ListPendingRequestsView.as_view(), name='list_pending_requests'),
]
