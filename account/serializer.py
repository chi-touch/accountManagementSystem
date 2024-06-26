from rest_framework import serializers
from .models import Account


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields =['account_number', 'first_name', 'last_name', 'account_balance', 'account_type']




class AccountCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields =['first_name', 'last_name', 'pin', 'account_type']


    #Note all this commented below can be used in replace of the above Meta class
    # account_number = serializers.CharField(max_length=10)
    # first_name = serializers.CharField(max_length=255)
    # last_name = serializers.CharField(max_length=255)
    # account_balance = serializers.DecimalField(max_digits=10, decimal_places=2)
    # account_type = serializers.CharField(max_length=10)
