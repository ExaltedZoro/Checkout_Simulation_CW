from uuid import uuid4
from random import randint


class Customer:

	def __init__(self):

		self.id = uuid4()
		self.basket_items = randint(1, 30)

		if self.basket_items >= 10:
			self.lottery = bool(randint(0, 1))
		else:
			self.lottery = False
