from rest_framework import serializers
from .models import ContactMessage


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        # fields = ['id', 'first_name', 'last_name', 'email', 'message', 'created_at']
        fields = '__all__'
