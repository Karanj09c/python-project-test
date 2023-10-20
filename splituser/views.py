from .models import Expense,ExpenseParticipant,User,Balance
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ParseError

import asyncio
from asgiref.sync import async_to_sync
from django.core.mail import send_mail

@async_to_sync
async def send_notification_email(user_email, subject, message):

    await asyncio.get_event_loop().run_in_executor(None, send_mail, subject, message, 'karanj09.cloudwapp@gmail.com', [user_email])

@api_view(['POST'])
def add_expense(request):
    data = request.data
    user_id = data['user_id']
    expense_type = data['expense_type']
    amount = data['amount']
    participants = data['participants']

    expense = Expense.objects.create(
        expense_type=expense_type,
        amount=amount,
    )

    share_per_person = 0
    subject = "Split User"
    message = "Partition Amount"
    if expense_type == Expense.EQUAL:
        share_per_person = amount / len(participants)
        for participant_id in participants:
            participant = User.objects.get(id=participant_id)
            ExpenseParticipant.objects.create(user=participant, expense=expense, share=share_per_person)

    elif expense_type == Expense.EXACT:
        for participant_data in participants:
            participant_id = participant_data['user_id']
            share = participant_data['share']
            participant = User.objects.get(id=participant_id)
            ExpenseParticipant.objects.create(user=participant, expense=expense, share=share)

    elif expense_type == Expense.PERCENT:
        total_percent = sum(participant_data['percent'] for participant_data in participants)
        if total_percent != 100:
            return Response({'error': 'Total percentage must be 100%'}, status=400)
        for participant_data in participants:

            participant_id = participant_data['user_id']
            percent_share = (amount * participant_data['percent']) / 100
            participant = User.objects.get(id=participant_id)

            ExpenseParticipant.objects.create(user=participant, expense=expense, share=percent_share)


    for participant_data in participants:
        participant_id = participant_data['user_id']
        share = participant_data['share'] if expense_type == Expense.EXACT else share_per_person
        participant = User.objects.get(id=participant_id)

        try:
            participant_balance = Balance.objects.get(user=participant, participant=user_id)
        except Balance.DoesNotExist:
            participant_balance = Balance(user=participant, participant=User.objects.get(id=user_id), balance=0)
        participant_balance.balance += share
        participant_balance.save()

        send_notification_email("karan@mailinator.com", subject, message)
    return Response(data)

@api_view(['GET'])
def get_user_balances(request, user_id):
    user = User.objects.get(id=user_id)
    balances = Balance.objects.filter(user=user, balance__gt=0)

    data = []
    for balance in balances:
        data.append({
            'user_id': balance.participant.userId,
            'balance': balance.balance,
        })

    return Response(data, status=200)


@api_view(['POST'])
def simplify_balances(request):
    user_id = request.data.get('user_id')

    # Get the user for whom you want to simplify balances
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)


    user_balances = Balance.objects.filter(user=user, balance__lt=0)
    user_participant_balances = Balance.objects.filter(participant=user, balance__gt=0)

    for balance in user_balances:
        for participant_balance in user_participant_balances:
            if balance.balance < 0 and participant_balance.balance > 0:

                transfer_amount = min(-balance.balance, participant_balance.balance)

                balance.balance += transfer_amount
                participant_balance.balance -= transfer_amount


                balance.save()
                participant_balance.save()

    return Response({'message': 'Balances simplified successfully'}, status=200)
