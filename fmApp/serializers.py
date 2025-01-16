from rest_framework import serializers
from .models import Table, Transaction, Category


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})


class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ['id', 'name', 'description', 'user']
        read_only_fields = ['id', 'user']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'type']


class TransactionSerializer(serializers.ModelSerializer):
    description = serializers.CharField(allow_blank=True, required=False)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())  # Используем PrimaryKeyRelatedField

    class Meta:
        model = Transaction
        fields = ['id', 'date', 'category', 'type', 'amount', 'description']

