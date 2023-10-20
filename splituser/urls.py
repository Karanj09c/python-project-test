from . import views
from django.urls import path

urlpatterns = [
    path('add_expense/', views.add_expense, name='add_expense'),
    path('get_user_balances/<str:user_id>/', views.get_user_balances, name='get_user_balances'),
    path('simplify_balances/', views.simplify_balances, name='simplify_balances'),
]
