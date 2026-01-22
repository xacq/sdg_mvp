from rest_framework import serializers
from .models import Category, RegexRule

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description"]

class RegexRuleSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = RegexRule
        fields = ["id", "name", "pattern", "enabled", "severity", "category", "category_name"]
