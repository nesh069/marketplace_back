from django.test import TestCase
from django.contrib.auth import get_user_model
from marketplace.models import Category, Listing, Favorite, Message

User = get_user_model()


class CategoryModelTests(TestCase):
    def test_category_creation(self):
        category = Category.objects.create(name='Electronics', slug='electronics')
        self.assertEqual(str(category), 'Electronics')


class ListingModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='seller',
            email='seller@example.com',
            password='pass123'
        )
        self.category = Category.objects.create(name='Phones', slug='phones')

    def test_listing_creation(self):
        listing = Listing.objects.create(
            seller=self.user,
            category=self.category,
            title='iPhone 14',
            description='Brand new iPhone',
            price=999.99
        )
        self.assertEqual(str(listing), 'iPhone 14')
        self.assertEqual(listing.status, 'active')


class FavoriteModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='buyer',
            email='buyer@example.com',
            password='pass123'
        )
        self.category = Category.objects.create(name='Laptops', slug='laptops')
        self.listing = Listing.objects.create(
            seller=self.user,
            category=self.category,
            title='MacBook Pro',
            description='M2 chip',
            price=1999.99
        )

    def test_favorite_creation(self):
        favorite = Favorite.objects.create(user=self.user, listing=self.listing)
        self.assertEqual(str(favorite), f'{self.user.email} -> MacBook Pro')
