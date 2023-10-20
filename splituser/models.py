# models.py

from django.db import models

class User(models.Model):
    userId = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=15)

class Expense(models.Model):
    EQUAL = 'EQUAL'
    EXACT = 'EXACT'
    PERCENT = 'PERCENT'
    EXPENSE_TYPE_CHOICES = [
        (EQUAL, 'Equal'),
        (EXACT, 'Exact'),
        (PERCENT, 'Percent'),
    ]

    name = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    expense_type = models.CharField(max_length=10, choices=EXPENSE_TYPE_CHOICES)
    participants = models.ManyToManyField(User, through='ExpenseParticipant')

class ExpenseParticipant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
    share = models.DecimalField(max_digits=10, decimal_places=2)


class Balance(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='balances')
    participant = models.ForeignKey('User', on_delete=models.CASCADE, related_name='participant_balances')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.name} owes {self.participant.name}: {self.balance}"
