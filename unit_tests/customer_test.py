# unit_test/customer_test.py

# Credits:
# -> Created by Olivia

# Unit tests for the Customer class

import unittest
from customer import Customer
from constants import REGULAR_PROCESS_TIME


class TestCustomer(unittest.TestCase):

    def test_basket_is_int(self):
        """Tests that the random number generated is an integer"""
        customer = Customer(1)
        self.assertIsInstance(customer.basket_items, int)

    def test_lottery_is_bool(self):
        """Tests that the lottery attribute is a boolean"""
        customer = Customer(1)
        self.assertIsInstance(customer.lottery, bool)

    def test_process_tick_removes_item(self):
        """Tests that a customer's basket item is removed when the time_elapsed reaches the process time"""
        customer = Customer(1)
        process = REGULAR_PROCESS_TIME
        old_value = customer.basket_items
        for i in range(process):
            customer.process_tick(process)
        self.assertTrue(customer.basket_items + 1 == old_value)


if __name__ == "__main__":
    unittest.main()
