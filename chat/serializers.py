from rest_framework import serializers
import datetime
import uuid
from .models import Conversation, Message


class WebhookSerializer(serializers.Serializer):
    TYPE_CHOICES = [
        ('NEW_CONVERSATION', 'New conversation'),
        ('NEW_MESSAGE', 'New message'),
        ('NEW_MESSAGE', 'New message'),
        ('CLOSE_CONVERSATION', 'Close conversation'),
    ]

    type = serializers.ChoiceField(choices=TYPE_CHOICES)
    timestamp = serializers.DateTimeField()
    data = serializers.DictField(
        child=serializers.JSONField(),
    )

    def validate_timestamp(self, value):
        """Valida se o timestamp é uma data/hora válida e não no futuro."""
        if value > datetime.datetime.now(datetime.timezone.utc):
            raise serializers.ValidationError("Timestamp cannot be in the future.")
        return value

    def validate(self, attrs):
        """Validações customizadas para o dicionário 'data'."""
        data = attrs.get('data', {})

        # If type is 'NEW_MESSAGE', checks if 'data' if a valid MessageSerializer
        if attrs['type'] == 'NEW_MESSAGE':
            message_serializer = MessageSerializer(data=data)
            if not message_serializer.is_valid():
                raise serializers.ValidationError({'data': message_serializer.errors})
        elif attrs['type'] == 'NEW_CONVERSATION':
            conversation_serializer = ConversationSerializer(data=data)
            if not conversation_serializer.is_valid():
                raise serializers.ValidationError(
                    {'data': conversation_serializer.errors}
                )
        else:
            conversation_serializer = ConversationClosedSerializer(data=data)
            if not conversation_serializer.is_valid():
                raise serializers.ValidationError(
                    {'data': conversation_serializer.errors}
                )
        return attrs


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'direction', 'content']

    def validate_direction(self, value):
        valid_directions = ['SENT', 'RECEIVED']
        if value not in valid_directions:
            raise serializers.ValidationError("Direction must be 'SENT' or 'RECEIVED'.")
        return value

    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError("Content cannot be empty.")
        return value

    def validate_id(self, value):
        try:
            uuid.UUID(str(value))  # Checks if is a valid UUID
            return value
        except ValueError:
            raise serializers.ValidationError("Invalid UUID format.")


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ['id']

    def validate_id(self, value):
        try:
            uuid.UUID(str(value))  # Checks if is a valid UUID
            return value
        except ValueError:
            raise serializers.ValidationError("Invalid UUID format.")


class ConversationClosedSerializer(ConversationSerializer):
    id = serializers.UUIDField()


class ConversationListSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'status', 'created_at', 'last_message', 'message_count']

    def get_last_message(self, obj):
        last_message = obj.messages.order_by('-timestamp').first()
        if last_message:
            return MessageSerializer(last_message).data
        return None

    def get_message_count(self, obj):
        return obj.messages.count()


class ConversationDetailSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ['id', 'status', 'created_at', 'messages']
