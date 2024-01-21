# customer.py

# Credits:
# -> Initial framework by Olivia
# -> Main code by Olivia
# -> Edits by Nate

# Includes the Customer class, which generates a random customer.
# Requires the simulation manager to pass an ID - assumed to be numerical.

from random import randint
from constants import SELF_SERVICE_PROCESS_TIME, REGULAR_PROCESS_TIME


class Customer:

	def __init__(self, id: int):
		self.id = id
		self.basket_items = randint(1, 30)

		self.time_elapsed = 0

		if self.basket_items >= 10:
			self.lottery = bool(randint(0, 1))
		else:
			self.lottery = False

	def display_details(self):
		"""A purely static method that only prints customer data."""
		print(f"C{self.id}:")
		print(f"-> Basket Items: {self.basket_items}")
		print(f"-> Time to process (cashier): {self.basket_items * SELF_SERVICE_PROCESS_TIME} seconds")
		print(f"-> Time to process (self-service): {self.basket_items * REGULAR_PROCESS_TIME} seconds")
		print(f"-> Lottery: {'has ticket!' if self.lottery else 'no ticket'}")

	def process_tick(self, process: int):
		"""Increments the number of ticks only when a customer is in a lane.
		When the customer hits a process time as given to them by a lane,
		one item in their basket is removed.
		This method is exclusively called by a Lane, which must also pass in a process integer,
		representing how long it takes to process an item.
		This method returns True if the customer should be removed from the lane after being full processed, and False otherwise"""
		self.time_elapsed += 1
		if self.time_elapsed % process == 0:
			self.basket_items -= 1
		if self.basket_items == 0:
			return True
		else:
			return False
