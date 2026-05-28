from rest_framework import serializers
from .models import MaintenanceTicket, TicketComment


class TicketCommentSerializer(serializers.ModelSerializer):
    author_email = serializers.EmailField(source='author.email', read_only=True)

    class Meta:
        model = TicketComment
        fields = ['id', 'ticket', 'author', 'author_email', 'text', 'created_at']
        read_only_fields = ['author', 'created_at']

    def create(self, validated_data):
        request = self.context['request']
        validated_data['author'] = request.user
        return super().create(validated_data)


class MaintenanceTicketSerializer(serializers.ModelSerializer):
    comments = TicketCommentSerializer(many=True, read_only=True)
    reported_by_email = serializers.EmailField(source='reported_by.email', read_only=True)
    assigned_to_email = serializers.EmailField(source='assigned_to.email', read_only=True)

    class Meta:
        model = MaintenanceTicket
        fields = [
            'id', 'property', 'reported_by', 'reported_by_email',
            'assigned_to', 'assigned_to_email', 'title', 'description',
            'priority', 'status', 'photo', 'comments',
            'created_at', 'updated_at', 'resolved_at'
        ]
        read_only_fields = ['reported_by', 'created_at', 'updated_at']

    def create(self, validated_data):
        request = self.context['request']
        validated_data['reported_by'] = request.user
        return super().create(validated_data)


class TicketStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceTicket
        fields = ['status', 'assigned_to', 'resolved_at']