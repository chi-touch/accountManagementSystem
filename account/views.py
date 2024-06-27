from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.status import HTTP_201_CREATED
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import Account, Transaction
from .serializer import AccountSerializer, AccountCreateSerializer
from decimal import Decimal


# Create your views here.

#the below is used to combine related views classes
class AccountViewSet(ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountCreateSerializer

#this class has being combined above in the AccountViewSet
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

#this class has being combined above in the AccountViewSet
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


@api_view(["POST"])
def deposit(request):
    account_number = request.data['account_number']
    amount = Decimal(request.data['amount'])
    account = get_object_or_404(Account, pk=account_number)
    # account.account_balance += Decimal(amount)
    account.account_balance += amount
    account.save()
    Transaction.objects.create(
        account=account,
        amount=amount,
    )
    return Response(data={"message": "Transaction successful"}, status=status.HTTP_200_OK)


@api_view(["POST"])
def withdraw(request):
    account_number = request.data['account_number']
    amount = request.data['amount']
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
