from time import perf_counter
from uuid import uuid4
from functools import reduce


class Lane:
	def __init__(self, process, capacity, opened=False):
		self.created = perf_counter()
		self.id = uuid4()
		self.is_regular = None
		self.customers = []
		self.customer_processed = False
		self.item_process = process
		self.open = opened
		self.capacity = capacity
		self.tick_counter = 0

	def increment_ticks(self):
		self.customer_processed = False
		self.tick_counter += 1
		if self.tick_counter == self.item_process:
			self.tick_counter = 0
			self.on_tick_reset()

	def on_tick_reset(self):
		if len(self.customers) > 0:
			self.customers[0].basket_items -= 1
			if self.customers[0].basket_items == 0:
				self.customers.pop(0)
				self.customer_processed = True
		if len(self.customers) == 0:
			self.open = False

	def data(self):
		customers = reduce(lambda x, y: x+f"* ({y.basket_items} items{', lotto' if y.lottery else ''}) ", self.customers, "")
		return {
			"id": self.id,
			"open": self.open,
			"type": "regular" if self.is_regular else "self-service",
			"customers": customers.strip(),
			"customer_processed": self.customer_processed
		}


class SelfServiceLane(Lane):
	def __init__(self, opened=False):
		super().__init__(6, 15, opened)
		self.is_regular = False


class RegularLane(Lane):
	def __init__(self, opened=False):
		super().__init__(4, 5, opened)
		self.is_regular = True
