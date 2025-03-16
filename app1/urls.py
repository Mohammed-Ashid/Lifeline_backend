from django.urls import path
from .views import NewFeedView,PendingFeedsView,signup,login,make_request,get_user_notifications,accept_notification,reject_notification,get_approved_requests,get_user_by_id

urlpatterns = [
    path('newfeed/', NewFeedView.as_view(), name='new-feed'),
    path('pending-feeds/', PendingFeedsView.as_view(), name='pending-feeds'),
    path('signup/', signup, name='signup'),
    path('login/', login, name='login'),
    path('makerequest/',make_request,name='make_request'),
    path('notifications/',get_user_notifications,name='get_user_notifications'),
    path('acceptNotification/', accept_notification, name='accept_notification'),
    path('rejectNotification/', reject_notification, name='reject_notification'),
    path('approvedRequests/', get_approved_requests, name='get_approved_requests'),
    path('users/<int:user_id>/', get_user_by_id, name='get_user_by_id'),
]