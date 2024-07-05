from email import message

from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.status import HTTP_201_CREATED
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Account, Transaction
from .serializer import AccountSerializer, AccountCreateSerializer, DepositWithdrawSerializer, WithdrawSerializer, \
    TransferSerializer
from decimal import Decimal
from .validators import validate_amount


# Create your views here.

# the below is used to combine related views classes
class AccountViewSet(ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountCreateSerializer


# this class has being combined above in the AccountViewSet
# class ListAccount(ListCreateAPIView):
#     queryset = Account.objects.all()
#     serializer_class = AccountCreateSerializer

# if u want to get the id by filtering u use get_queryset
# def get_queryset(self):
#     return Account.objects.all()
#
# def get_serializer_class(self):
#     return AccountCreateSerializer

# the below replaces te above to make it different
# def get(self,request):
#     accounts = Account.objects.all()
#     serializer = AccountCreateSerializer(accounts,many=True)
#     return Response(serializer.data, status= status.HTTP_200_OK)
#
# def post(self, request):
#     serializer = AccountCreateSerializer(data=request.data)
#     serializer.is_valid(raise_exception=True)
#     serializer.save()
#     return Response(serializer.data, status=HTTP_201_CREATED)


# @api_view(['GET', 'POST'])
# def list_account(request):
#     if request.method == 'GET':
#         accounts = Account.objects.all()
#         serializer = AccountSerializer(accounts, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     elif request.method == 'POST':
#         serializer = AccountCreateSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=HTTP_201_CREATED)
#

# this class has being combined above in the AccountViewSet
# class AccountDetail(RetrieveUpdateDestroyAPIView):
#     queryset = Account.objects.all()
#     serializer_class = AccountCreateSerializer


# def get(self,request,pk):
#     account = get_object_or_404(Account, pk=pk)
#     serializer = AccountSerializer(account)
#     return Response(serializer.data, status=status.HTTP_200_OK)
#
# def put(self,request,pk):
#     account = get_object_or_404(Account, pk=pk)
#     serializer = AccountSerializer(account, data=request.data)
#     serializer.is_valid(raise_exception=True)
#     serializer.save()
#     return Response(serializer.data, status=status.HTTP_200_OK)
#
# def delete(self,request,pk):
#     account = get_object_or_404(Account, pk=pk)
#     account.delete()
#     return Response(status=status.HTTP_204_NO_CONTENT)
#


# @api_view(["GET", "PUT", "PATCH", "DELETE"])
# def account_details(request, pk):
#     account = get_object_or_404(Account, pk=pk)
#     if request.method == "GET":
#         serializer = AccountSerializer(account)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     elif request.method == "PUT":
#         serializer = AccountSerializer(account, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     elif request.method == "DELETE":
#         account.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


class Deposit(APIView):
    def post(self, request):
        serializer = DepositWithdrawSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        account_number = serializer.data['account_number']
        amount = Decimal(serializer.data['amount'])

        # self.validate_amount(amount)

        transaction_details = {}
        account = get_object_or_404(Account, pk=account_number)
        balance = account.account_balance
        balance += amount
        Account.objects.filter(account_number=account_number).update(account_balance=balance)

        Transaction.objects.create(
            account=account,
            amount=amount,
        )

        transaction_details['account_number'] = account_number
        transaction_details['amount'] = amount
        transaction_details['transaction_type'] = 'CREDIT'
        return Response(data=transaction_details, status=status.HTTP_200_OK)


# @api_view(["POST"])
# def deposit(request):
#     account_number = request.data['account_number']
#     amount = Decimal(request.data['amount'])
#     account = get_object_or_404(Account, pk=account_number)
#     # account.account_balance += Decimal(amount)
#     account.account_balance += amount
#     account.save()
#     Transaction.objects.create(
#         account=account,
#         amount=amount,
#     )
#     return Response(data={"message": "Transaction successful"}, status=status.HTTP_200_OK)


class Withdraw(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer = WithdrawSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        account_number = request.data['account_number']
        amount = request.data['amount']
        if validate_amount(amount):
            return Response(data={"message": "Negative amount can not be withdrawn"},
                            status=status.HTTP_400_BAD_REQUEST)
        pin = request.data["pin"]
        account = get_object_or_404(Account, pk=account_number)
        if account.pin == pin:
            if account.account_balance > amount:
                account.account_balance -= Decimal(amount)
                account.save()
                Transaction.objects.create(
                    account=account,
                    amount=amount,
                    transaction_type='DEB'
                )
            else:
                return Response(data={"message": "Insufficient"}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(data={"message": "Invalid pin"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data={"message": "Withdraw successful"}, status=status.HTTP_200_OK)


class TransferViewSet(ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = TransferSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        user = request.user
        serializer = TransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sender_account = serializer.data['sender_account']
        receiver_account = serializer.data['receiver_account']
        amount = Decimal(serializer.data['amount'])
        transaction_details = {}

        sender_account_from = get_object_or_404(Account, pk=sender_account)
        receiver_account_to = get_object_or_404(Account, pk=receiver_account)
        balance = sender_account_from.account_balance
        if balance > amount:
            balance -= amount
            Account.objects.filter(pk=sender_account).update(account_balance=balance)
        else:
            return Response(data={"message": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            transaction_balance = receiver_account_to.account_balance + amount
            Account.objects.filter(pk=receiver_account).update(account_balance=transaction_balance)
        except Account.DoesNotExist:
            return Response(data={"message": "Transfer failed"}, status=status.HTTP_400_BAD_REQUEST)
        # Transaction.objects.create(
        #     account=sender_account_from,
        #     amount=amount,
        #     transaction_type='TRANSFER'
        # )
        transaction_details['receiver_account'] = receiver_account
        transaction_details['amount'] = amount
        transaction_details['transaction_type'] = 'TRANSFER'
        return Response(data=transaction_details, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        return Response(data="Method not supported", status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def list(self, request, *args, **kwargs):
        return Response(data="Method not supported", status=status.HTTP_405_METHOD_NOT_ALLOWED)


class CheckBalance(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        account = get_object_or_404(Account, user=user.id)
        balance_details = {}
        balance_details['account number'] = account.account_number
        balance_details['balance'] = account.account_balance
        message = f'''
        your new balance is
        {account.account_balance}
        thank you for banking with jaguda'''
        send_mail("JAGUDA BANK",
                  message=message,
                  from_email='noreply@jaguda.com',
                  recipient_list=[f'{user.email}'])
        return Response(data=balance_details, status=status.HTTP_200_OK)
