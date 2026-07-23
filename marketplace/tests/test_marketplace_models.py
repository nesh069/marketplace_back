from django.test import TestCase
from django.contrib.auth import get_user_model
from marketplace.models import Category, Listing, Favourite

User = get_user_model()


class CategoryModelTests(TestCase):
    def test_category_creation(self):
        category = Category.objects.create(name='Electronics')
        self.assertEqual(str(category), 'Electronics')


class ListingModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='seller',
            email='seller@example.com',
            password='pass123'
        )
        self.category = Category.objects.create(name='Phones')

    def test_listing_creation(self):
        listing = Listing.objects.create(
            seller=self.user,
            category=self.category,
            title='iPhone 14',
            description='Brand new',
            price=999.99
        )
        self.assertEqual(str(listing), 'iPhone 14 (Available)')


class FavouriteModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='buyer',
            email='buyer@example.com',
            password='pass123'
        )
        self.category = Category.objects.create(name='Laptops')
        self.listing = Listing.objects.create(
            seller=self.user,
            category=self.category,
            title='MacBook Pro',
            description='M2 chip',
            price=1999.99
        )

    def test_favourite_creation(self):
        favourite = Favourite.objects.create(user=self.user, listing=self.listing)
        self.assertIn('buyer@example.com', str(favourite))
