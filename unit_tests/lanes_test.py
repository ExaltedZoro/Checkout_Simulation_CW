import unittest

from customer import Customer
from lanes import RegularLane


class LaneUnitTest(unittest.TestCase):
    def setUp(self):
        self.lane = RegularLane(1, True)

    def test_open_and_close(self):
        self.assertEqual(self.lane.is_open(), True, "Should be open")
        self.lane.close()
        self.assertEqual(self.lane.is_open(), False, "Should be closed")
        self.lane.open()
        self.assertEqual(self.lane.is_open(), True, "Should be open")

    def test_queues(self):
        self.lane.add_customer(Customer(1))
        self.lane.add_customer(Customer(2))
        self.lane.add_customer(Customer(3))
        self.assertEqual(self.lane.can_accept_customers(), True, "Should be able to accept customers")
        self.lane.add_customer(Customer(4))
        self.lane.add_customer(Customer(5))
        self.assertEqual(self.lane.can_accept_customers(), False, "Should not be able to accept customers")
        self.assertEqual(self.lane.queue_size(), 5, "Queue size should be 5")
        self.lane.pop()
        self.assertEqual(self.lane.queue_size(), 4, "Queue size should be 4")




