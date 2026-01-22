from rest_framework import serializers
from .models import Document, Finding

class DocumentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["id", "original_name", "file"]

    def create(self, validated_data):
        request = self.context["request"]
        return Document.objects.create(
            original_name=validated_data["original_name"],
            file=validated_data["file"],
            uploaded_by=request.user,
        )

class FindingSerializer(serializers.ModelSerializer):
    rule_name = serializers.CharField(source="rule.name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Finding
        fields = ["id", "rule_name", "category_name", "match_text", "start_index", "end_index", "created_at"]

class DocumentDetailSerializer(serializers.ModelSerializer):
    findings = FindingSerializer(many=True, read_only=True)
    classified_category_name = serializers.CharField(source="classified_category.name", read_only=True)

    class Meta:
        model = Document
        fields = [
            "id", "original_name", "uploaded_at", "risk_score",
            "classified_category_name", "findings"
        ]
