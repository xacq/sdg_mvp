# alerts/views.py
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from .models import Alert
from rest_framework import serializers

class AlertSerializer(serializers.ModelSerializer):
    document_name = serializers.CharField(source="document.original_name", read_only=True)
    class Meta:
        model = Alert
        fields = ["id", "document", "document_name", "title", "severity", "status", "details", "created_at"]

class AlertListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Alert.objects.select_related("document").order_by("-created_at")
    serializer_class = AlertSerializer
