# audit/views.py
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from .models import AuditEvent
from rest_framework import serializers

class AuditSerializer(serializers.ModelSerializer):
    actor_username = serializers.CharField(source="actor.username", read_only=True)

    class Meta:
        model = AuditEvent
        fields = ["id", "created_at", "event_type", "actor_username", "object_type", "object_id", "message", "meta_json"]

class AuditListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = AuditEvent.objects.select_related("actor").order_by("-created_at")
    serializer_class = AuditSerializer
