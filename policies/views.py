# policies/views.py
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from .models import Category, RegexRule
from .serializers import CategorySerializer, RegexRuleSerializer

class CategoryListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer

class RuleListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = RegexRule.objects.select_related("category").all().order_by("name")
    serializer_class = RegexRuleSerializer
