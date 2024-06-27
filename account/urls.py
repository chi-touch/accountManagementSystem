from django.urls import path, include
from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()
router.register('accounts', views.AccountViewSet)

print(router.urls)

urlpatterns = [
    path('',include(router.urls)),
    #the below is combined to be the one above
    # path('accounts', views.ListAccount.as_view()),
    # path('accounts/<str:pk>', views.AccountDetail.as_view()),
    path('deposit',views.deposit),
    path('withdraw',views.withdraw)
]


