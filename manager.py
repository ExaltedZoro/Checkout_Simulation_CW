import math
import time
from random import randint
from time import perf_counter
from time import sleep
import asyncio

from lanes import RegularLane, SelfServiceLane
from customer import Customer

"""
TO-DO
Balancing lanes - DONE
Add logic to assign customers to the shortest queue possible out of available open lanes - SHOULD BE DONE
Make self service process items are different times (move logic out of the lane and to the customer) - DONE
"""


class SimulationManager:

	def __init__(self):

		self.running = False
		self.start_time = None
		self.duration = 60.0
		self.elapsed = 0

		self.total_customers_seen = 0
		self.total_customers_processed = 0
		self.lanes = [
			SelfServiceLane(True),
			RegularLane(1, True),
			RegularLane(2),
			RegularLane(3),
			RegularLane(4),
			RegularLane(5)
		]

		self.lost_customers = []

	async def start_sim(self):
		self.running = True
		self.start_time = perf_counter()
		while True:
			for i in range(30):
				await self.sim_loop()
				# time.sleep(1)
				input()
			print("Would you like to continue the simulation?")
			carry_on = input("Y/N: ")
			if carry_on == "N":
				break

		print("Simulation ended")
		print(f"Total customers seen: {self.total_customers_seen}")
		print(f"Total customers processed: {self.total_customers_processed}\n")
		print("Lane status at simulation end")
		self.output_lanes()

	async def sim_loop(self):
		"""The brain of the program.
		Generates customers, assigns them to lanes and then increments each of those lanes"""

		# Use this to enable an actual timer-thing
		# await asyncio.sleep(1.0)
		self.elapsed += 1.0

		if self.elapsed == 1.0:
			# If it's the first tick of the simulation, up to 10 customers are generated
			customers = randint(1, 10)
			self.lost_customers += [Customer() for i in range(0, customers)]
			self.total_customers_seen += customers
			for customer in self.lost_customers:
				print(f"Customer {customer.id} generated with {customer.basket_items} items{' and a lotto ticket!' if customer.lottery else ''}\n")
		elif randint(1, 5) == 1:
			# Each tick after the first has a 20% chance of generating a customer
			customer = Customer()
			print(f"Customer {customer.id} generated with {customer.basket_items} items{' and a lotto ticket!' if customer.lottery else ''}\n")
			self.lost_customers.append(customer)
			self.total_customers_seen += 1

		open_lanes = self.get_open_lanes()

		# A separate list used to store the customers that have been moved into a lane during this tick
		# Removes any issues from the for loop to do with modifying the list it's iterating through during iteration
		assigned_customers = []

		for customer in self.lost_customers:
			# If the customers is able to enter self-service, the program attempts to add them to it regardless
			if customer.basket_items < 10:
				self_service = self.lanes[0]
				if self_service.can_accept_customers():
					self_service.customers.append(customer)
					# Add the customer to a separate list to be removed later.
					# Stops the for loop messing up because the list is modified mid-loop
					assigned_customers.append(customer)
					print(f"Customer {customer.id} with {customer.basket_items} basket items assigned to Self-Service\n")
					continue

			available_regular_lanes = []
			for i in range(1, len(self.lanes)):
				# For loop creates a list of currently open regular lanes
				if self.lanes[i].can_accept_customers() & self.lanes[i].is_regular:
					available_regular_lanes.append(self.lanes[i])
			# If there are no available regular lanes, we open a new one and add it to the list
			if not available_regular_lanes:
				opened_lane = self.open_lane()
				available_regular_lanes.append(opened_lane)

			# Initialise the lane with the shortest queue to a default value
			shortest_queue = available_regular_lanes[0]
			for lane in available_regular_lanes:
				# If the current shortest queue is larger than the new queue, the new lane becomes the shortest
				if lane.queue_size() < shortest_queue.queue_size():
					shortest_queue = lane
			shortest_queue.customers.append(customer)
			assigned_customers.append(customer)
			print(f"Customer {customer.id} with {customer.basket_items} basket items {'and a lotto ticket ' if customer.lottery else ''}assigned to {f'Lane {shortest_queue.id}' if shortest_queue.is_regular else 'Self-Service'}\n")

		# The customers that were assigned to lanes this tick are removed from the lost customers list
		for customer in assigned_customers:
			self.lost_customers.remove(customer)

		# Advances the ticks for each lane and adds any customers that were processed to the total processed count
		for lane in open_lanes:
			lane.increment_ticks()
			self.total_customers_processed += int(lane.customer_processed)

		self.balance_lanes()

		print(f"Current unassigned customer count: {len(self.lost_customers)}")
		print(f"Current processed customer count: {self.total_customers_processed}")
		print(f"Tick {self.elapsed} complete")

		# Output the lanes every 30 seconds
		if self.elapsed % 30 == 0:
			self.format_output()

	def format_output(self):
		"""Formats and outputs the current lane status and customer counts"""

		customers_processed = self.output_lanes()

		self.total_customers_processed += customers_processed
		print("--------------------------------------")
		print(f"Tick {self.elapsed} / {self.duration}")
		print(f"Customers waiting this tick: {len(self.lost_customers)}")
		print(f"Customers processed this tick: {customers_processed}")
		print("\n")

	def output_lanes(self):
		"""Part of the format_output method. Made separate to allow the simulation end to use just this bit"""
		customers_processed = 0

		for lane in self.lanes:
			data = lane.data()
			customers_processed += int(data["customer_processed"])
			print(f"{data['type']} Lane {data['id'] if data['type'] == 'Cashier' else ''} - {data['customers'] if data['open'] else 'Closed'}")

		return customers_processed

	def get_open_lanes(self, include_self_service=True):
		"""Returns a list of currently open lanes. Excludes self-service if False given in arguments"""
		open_lanes = []
		for lane in self.lanes:
			if include_self_service:
				if lane.is_open():
					open_lanes.append(lane)
			else:
				if lane.is_open() & lane.is_regular:
					open_lanes.append(lane)

		return open_lanes

	def open_lane(self):
		"""Searches the list for a closed lane, opens it and returns it"""
		for lane in self.lanes:
			if not lane.is_open():
				lane.open()
				return lane
		return None

	def balance_lanes(self):
		"""Moves customers from longer lanes to shorter ones. Ignore self-service entirely"""
		open_lanes = self.get_open_lanes(False)
		total_customers = 0
		for lane in open_lanes:
			total_customers += lane.queue_size()
		# Taking the average queue size of each open lane and then finding the closest integer both above and below it
		# guarantees that when as balanced as possible each lane will either have a queue size of the integer above the
		# average or the integer below the average
		average_queue = total_customers / len(open_lanes)
		upper = math.ceil(average_queue)
		lower = math.floor(average_queue)
		for lane in open_lanes:
			for lane_2 in open_lanes:
				while lane.queue_size() > upper:
					if lane_2.queue_size() < lower:
						customer = lane.customers.pop()
						lane_2.customers.append(customer)
						print(f"Customer {customer.id} moved from Lane {self.lanes.index(lane)} to {self.lanes.index(lane_2)}")
					else:
						break
