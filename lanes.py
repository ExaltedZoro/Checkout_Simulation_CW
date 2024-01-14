from time import perf_counter
from uuid import uuid4
from functools import reduce


class Lane:
	def __init__(self, capacity, opened=False):
		self.created = perf_counter()
		self.id = uuid4()
		self.is_regular = None
		self.customers = []
		self.customer_processed = False
		self.opened = opened
		self.capacity = capacity

	def increment_ticks(self):
		"""Ticks all customers that need ticking"""
		self.customer_processed = False
		if len(self.customers) == 0:
			return
		remove_customer = self.customers[0].tick_cashier()
		if remove_customer:
			self.customers.pop(0)
			self.output_customer_processed()
			self.customer_processed = True

	def output_customer_processed(self):
		"""Lets the user know that a customer has been processed and removed from a lane"""
		print(f"Customer finished checkout at {'Cashier' if self.is_regular else 'Self-Service'} Lane")

	def data(self):
		"""Returns a dictionary of the lanes data"""
		customers = reduce(lambda x, y: x+f"* ({y.basket_items} items{', lotto' if y.lottery else ''}) ", self.customers, "")
		return {
			"id": self.id,
			"open": self.opened,
			"type": "Cashier" if self.is_regular else "Self-Service",
			"customers": customers.strip(),
			"customer_processed": self.customer_processed
		}

	def queue_size(self):
		"""Returns the length of the lanes customer list"""
		return len(self.customers)

	def can_accept_customers(self):
		"""Returns whether the queue size is below capacity and the lane is open"""
		return len(self.customers) < self.capacity and self.is_open()

	def open(self):
		"""Opens the lane"""
		self.opened = True
		print(f"{f'Lane {self.id}' if self.is_regular else 'Self-Service'} opened\n")

	def close(self):
		"""Closes the lane"""
		self.opened = False
		print(f"{f'Lane {self.id}' if self.is_regular else 'Self-Service'} closed\n")

	def is_open(self):
		"""Returns whether the lane is open or closed"""
		return self.opened


class SelfServiceLane(Lane):
	def __init__(self, opened=False):
		super().__init__(15, opened)
		self.is_regular = False
		self.customer_processed = 0

	def increment_ticks(self):
		customers_to_remove = []
		self.customer_processed = 0
		if len(self.customers) == 0:
			self.close()
			return

		for i in range(min(8, len(self.customers))):
			customer = self.customers[i]
			remove_customer = customer.tick_self_service()
			if remove_customer:
				# Checks if there is a customer that is not currently at a till
				if len(self.customers) > 8:
					# The 9th customer in the queue is moved to the space of the customer that has just finished
					self.customers.insert(i, self.customers.pop(8))
					# Finished customer is removed from the list
					self.customers.remove(customer)
					# Other list indexes are not altered by this, leaving the for loop untouched
				else:
					# If the queue size is not above 8, removing the customer from the list would mess with the for loop
					# so, we add it to a separate list to be removed later
					customers_to_remove.append(customer)
				print(f"Customer {customer.id} finished checkout at Self Service")
				self.customer_processed += 1

		# Iterates through the finished customers and removes them from the lane
		if len(customers_to_remove) != 0:
			for customer in customers_to_remove:
				self.customers.remove(customer)

		# If the lane queue is empty, close the lane automatically
		if len(self.customers) == 0:
			self.close()


class RegularLane(Lane):
	def __init__(self, number, opened=False):
		super().__init__(5, opened)
		self.is_regular = True
		self.id = number
