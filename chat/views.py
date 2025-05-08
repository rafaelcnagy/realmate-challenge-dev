from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from .models import Conversation, Message
from .serializers import (
    WebhookSerializer,
    ConversationListSerializer,
    ConversationDetailSerializer,
)
import uuid


class WebhookView(APIView):
    def post(self, request):
        data = request.data
        serializer = WebhookSerializer(data=request.data)
        if serializer.is_valid():
            event_type, timestamp, event_data = serializer.validated_data.values()
            if event_type == 'NEW_CONVERSATION':
                conversation_id = uuid.UUID(event_data['id'])
                Conversation.objects.create(
                    id=conversation_id,
                    status=Conversation.Status.OPEN,
                    opened_at=timestamp,
                )

                return Response({'status': 'success'}, status=status.HTTP_201_CREATED)

            elif event_type == 'NEW_MESSAGE':
                conversation_id = uuid.UUID(event_data['conversation_id'])
                conversation = get_object_or_404(Conversation, id=conversation_id)

                if conversation.status == Conversation.Status.CLOSED:
                    return Response(
                        {'error': 'Cannot add messages to a closed conversation'},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                Message.objects.create(
                    id=uuid.UUID(event_data['id']),
                    conversation=conversation,
                    direction=event_data['direction'],
                    content=event_data['content'],
                    timestamp=timestamp,
                )

                return Response({'status': 'success'}, status=status.HTTP_201_CREATED)

            elif event_type == 'CLOSE_CONVERSATION':
                conversation_id = uuid.UUID(event_data['id'])
                conversation = get_object_or_404(Conversation, id=conversation_id)
                if conversation.status == Conversation.Status.CLOSED:
                    return Response(
                        {'error': 'This conversation is already closed'},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                conversation.status = Conversation.Status.CLOSED
                conversation.closed_at = timestamp
                conversation.save()
                return Response({'status': 'success'}, status=status.HTTP_200_OK)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConversationListView(generics.ListAPIView):
    queryset = Conversation.objects.all().order_by('-created_at')
    serializer_class = ConversationListSerializer


class ConversationDetailView(generics.RetrieveAPIView):
    queryset = Conversation.objects.all()
    serializer_class = ConversationDetailSerializer
    lookup_field = 'id'
