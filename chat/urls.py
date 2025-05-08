from django.urls import path
from .views import ConversationListView, ConversationDetailView, WebhookView

urlpatterns = [
    path('webhook/', WebhookView.as_view()),
    path('conversations/', ConversationListView.as_view(), name='conversation-list'),
    path(
        'conversations/<uuid:id>/',
        ConversationDetailView.as_view(),
        name='conversation-detail',
    ),
]
