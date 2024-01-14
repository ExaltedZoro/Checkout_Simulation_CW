from uuid import uuid4
from random import randint


class Customer:

	def __init__(self, id):
		self.id = id
		self.basket_items = randint(1, 30)

		self.time_at_cashier = self.basket_items * 4
		self.time_at_self_service = self.basket_items * 6

		if self.basket_items >= 10:
			self.lottery = bool(randint(0, 1))
		else:
			self.lottery = False

	def tick_self_service(self):
		"""Ticks the customer as if they're in a self-service lane.
		It returns True if basket items is 0, otherwise False"""
		self.time_at_self_service -= 1
		if self.time_at_self_service % 6 == 0:
			self.basket_items -= 1
		if self.basket_items == 0:
			return True
		else:
			return False

	def tick_cashier(self):
		"""Ticks the customer as if they're in a cashier lane.
		It returns True if basket items is 0, otherwise False"""
		self.time_at_cashier -= 1
		if self.time_at_cashier % 4 == 0:
			self.basket_items -= 1
		if self.basket_items == 0:
			return True
		else:
			return False


