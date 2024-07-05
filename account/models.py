from django.db import models
from django.conf import settings
from .utility import generate_account_number
from .validators import validate_pin


# django give primary key by default
# Create your models here.

class Account(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    account_number = models.CharField(max_length=10,
                                      default=generate_account_number,
                                      unique=True,
                                      primary_key=True)

    pin = models.CharField(max_length=4, validators=[validate_pin], default='0000')
    account_balance = models.DecimalField(max_digits=15,
                                          decimal_places=2,
                                          default=0.00)
    ACCOUNT_TYPE = [
        ('S', 'SAVINGS'),
        ('C', 'CURRENT'),
        ('D', 'DOM'),

    ]
    account_type = models.CharField(max_length=1,
                                    choices=ACCOUNT_TYPE,
                                    default='S')
    transactions = models.ManyToOneRel

    def __str__(self):
        return f"{self.account_type} {self.account_balance}"

    def first_name(self):
        return self.user


class Transaction(models.Model):
    TRANSACTION_TYPE = [
        ('DEB', 'DEBIT'),
        ('CRE', 'CREDIT'),
        ('TRA', 'TRANSFER')
    ]

    TRANSACTION_STATUS = [
        ('S', 'SUCCESSFUL'),
        ('F', 'FAIL'),
        ('P', 'PENDING')
    ]

    account = models.ForeignKey(Account, on_delete=models.CASCADE,
                                related_name='transactions')

    transaction_type = models.CharField(max_length=3,
                                        choices=TRANSACTION_TYPE,
                                        default='CRE')

    transaction_time = models.DateTimeField(auto_now_add=True)
    # this is when amount is in interger not in string
    # amount = models.DecimalField(max_digits=15, decimal_places=2)
    amount = models.CharField(max_length=25)
    description = models.CharField(max_length=255,blank=True,default="description not provided")
    transaction_status = models.CharField(max_length=1,
                                          choices=TRANSACTION_STATUS,
                                          default='S')
