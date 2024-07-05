from rest_framework import serializers
from .models import Account, Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'amount', 'transaction_type', 'transaction_time', 'transaction_status', 'description']


class AccountSerializer(serializers.ModelSerializer):
    transactions = TransactionSerializer(many=True)

    class Meta:
        model = Account
        fields = ['account_number', 'account_balance', 'account_type', 'transactions']
        transactions = serializers.StringRelatedField()


class AccountCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['user', 'account_number', 'pin', 'account_type']

    # Note all this commented below can be used in replace of the above Meta class
    # account_number = serializers.CharField(max_length=10)
    # first_name = serializers.CharField(max_length=255)
    # last_name = serializers.CharField(max_length=255)
    # account_balance = serializers.DecimalField(max_digits=10, decimal_places=2)
    # account_type = serializers.CharField(max_length=10)


class DepositWithdrawSerializer(serializers.Serializer):
    account_number = serializers.CharField(max_length=10)
    amount = serializers.DecimalField(max_digits=20, decimal_places=2)


class WithdrawSerializer(serializers.Serializer):
    account_number = serializers.CharField(max_length=10)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    pin = serializers.CharField(max_length=10)


class TransferSerializer(serializers.Serializer):
    sender_account = serializers.CharField(max_length=10)
    receiver_account = serializers.CharField(max_length=10)
    amount = serializers.DecimalField(max_digits=20, decimal_places=2)
    # pin = serializers.CharField(max_length=10)
