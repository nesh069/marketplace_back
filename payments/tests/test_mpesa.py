from django.test import TestCase
from django.contrib.auth import get_user_model
from marketplace.models import Category, Listing
from payments.models import Transaction

User = get_user_model()


class TransactionModelTests(TestCase):
    def setUp(self):
        self.buyer = User.objects.create_user(
            username='buyer',
            email='buyer@example.com',
            password='pass123'
        )
        self.category = Category.objects.create(name='Phones', slug='phones')
        self.listing = Listing.objects.create(
            seller=self.buyer,
            category=self.category,
            title='iPhone',
            description='New',
            price=500.00
        )

    def test_transaction_creation(self):
        transaction = Transaction.objects.create(
            buyer=self.buyer,
            listing=self.listing,
            amount=500.00
        )
        self.assertEqual(transaction.status, 'pending')
        self.assertEqual(str(transaction), f'Transaction {transaction.id} - pending')
