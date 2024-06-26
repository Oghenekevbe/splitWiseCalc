from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Expense, ExpenseSharing
from services.expense_services import *
import uuid


User = get_user_model()


class TestCreateExpenseView(APITestCase):

    def setUp(self):
        self.client = APIClient()
        # Create a user
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.client.force_authenticate(user=self.user)  # Authenticate the user

    def test_create_expense_valid_data(self):
        data = {
            'transaction_id': '0176c404-6f1a-4c5b-ae4c-003348b8c9f6',
            'paid_by' : self.user.id,
            'title': 'Test Expense',
            'description': 'This is a test expense',
            'amount': 100.00,
            
        }
        data['paid_by'] = self.user.id
        response = self.client.post('/api/create_expense/', data, format='json')
        print('response = ', response)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Expense.objects.count(), 1)
        self.assertEqual(Expense.objects.get().title, data['title'])

    def test_create_expense_invalid_data(self):
        data = {
            'title': '',  # Empty title
             'transaction_id': '0176c404-6f1a-4c5b-ae4c-003348b8c9f6',
            'description': 'This is a test expense',
            'paid_by' : self.user.id,
            'amount': 100.00
        }
        response = self.client.post('/api/create_expense/', data, format ='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Expense.objects.count(), 0)

    def test_create_expense_unauthenticated(self):
        self.client.force_authenticate(user=None)
        data = {
            'title': '',  # Empty title
             'transaction_id': '0176c404-6f1a-4c5b-ae4c-003348b8c9f6',
            'description': 'This is a test expense',
            'paid_by' : self.user.id,
            'amount': 100.00
        }
        response = self.client.post('/api/create_expense/', data, format = 'json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)



class ListExpensesViewTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        # Create a user
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.client.force_authenticate(user=self.user)  # Authenticate the user

        # Create some test expenses with UUID transaction_ids
        Expense.objects.create(
            transaction_id=uuid.uuid4(),
            paid_by=self.user,
            title="Expense 1",
            description="Test expense 1",
            amount=50.0
        )
        Expense.objects.create(
            transaction_id=uuid.uuid4(),
            paid_by=self.user,
            title="Expense 2",
            description="Test expense 2",
            amount=100.0
        )



    def test_list_expenses(self):
        response = self.client.get('/api/expenses/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Assuming you expect 2 expenses created in setUp
        self.assertEqual(response.data[0]['title'], "Expense 1")
        self.assertEqual(response.data[1]['title'], "Expense 2")


    def test_get_single_expense(self):
        expense_id = 1  # Replace with an existing expense ID
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/expenses/{expense_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Add assertions for the response data








class TestCalculateExpenseSharingValues(TestCase):
    def test_equal_sharing(self):
        method = 'EQUAL'
        amount = 100.00
        values = []
        total_shares = 2
        expected_shares = [50.00, 50.00]

        shares = calculate_expense_sharing_values(method, amount, values, total_shares)
        self.assertEqual(shares, expected_shares)

    def test_exact_sharing(self):
        method = 'EXACT'
        amount = 100.00
        values = [40.00, 60.00]
        total_shares = 2
        expected_shares = [40.00, 60.00]

        shares = calculate_expense_sharing_values(method, amount, values, total_shares)
        self.assertEqual(shares, expected_shares)

    def test_percent_sharing(self):
        method = 'PERCENT'
        amount = 100.00
        values = [40, 60]
        total_shares = 2
        expected_shares = [40.00, 60.00]

        shares = calculate_expense_sharing_values(method, amount, values, total_shares)
        self.assertEqual(shares, expected_shares)

    def test_invalid_method(self):
        method = 'INVALID'
        amount = 100.00
        values = []
        total_shares = 2

        with self.assertRaises(ValueError):
            calculate_expense_sharing_values(method, amount, values, total_shares)






