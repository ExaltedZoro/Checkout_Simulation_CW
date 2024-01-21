# manager.py

# Credits:
# -> Initial framework by Olivia
# -> 50/50 split on contribution by Olivia and Nate

# Simulation manager class
# -> Determines if the simulation is running and when to stop
# -> Formats and outputs data from lanes and customers

import math
import time
from random import randint
from time import perf_counter

from lanes import RegularLane, SelfServiceLane
from customer import Customer

from constants import SELF_SERVICE_PROCESS_TIME, REGULAR_PROCESS_TIME


class SimulationManager:
	def __init__(self):
		self.running = False
		self.start_time = None
		self.elapsed = 0

		self.total_customers_seen = 0
		self.total_customers_processed = 0

		self.lanes = [
			SelfServiceLane(1, True),
			RegularLane(2, True),
			RegularLane(3),
			RegularLane(4),
			RegularLane(5),
			RegularLane(6)
		]

		self.lost_customers = []

	def start_sim(self):
		self.running = True
		self.start_time = perf_counter()
		while self.running:
			for i in range(30):
				self.sim_loop()
				time.sleep(1)
			print("Would you like to continue the simulation?")
			carry_on = input("Y/N: ")
			if carry_on == "N":
				self.running = False

		print("\n-- Simulation ended --")
		print(f"Total customers seen: {self.total_customers_seen}")
		print(f"Total customers processed: {self.total_customers_processed}\n")
		print("Lane status at simulation end")

		self.output_lanes()

	def sim_loop(self):
		"""The brain of the program.
		Generates customers, assigns them to lanes and then increments each of those lanes"""

		self.elapsed += 1

		if self.elapsed == 1:
			# If it's the first tick of the simulation, up to 10 customers are generated
			customers = randint(1, 10)
			self.lost_customers += [Customer(i + 1) for i in range(customers)]
			self.total_customers_seen += customers
			for customer in self.lost_customers:
				self.introduce_customer(customer)

		elif randint(1, 10) == 1:
			# Each tick after the first has a 10% chance of generating a customer
			self.total_customers_seen += 1
			customer = Customer(self.total_customers_seen)
			self.introduce_customer(customer)
			self.lost_customers.append(customer)

		open_lanes = self.get_open_lanes()

		# A separate list used to store the customers that have been moved into a lane during this tick
		# Removes any issues from the for loop to do with modifying the list it's iterating through during iteration
		assigned_customers = []

		for customer in self.lost_customers:
			# If the customer is able to enter self-service, the program attempts to add them to it regardless of status
			if customer.basket_items < 10:
				self_service = self.lanes[0]
				# If self-service is not full, we add the customer to it regardless of other circumstances,
				# which includes opening it specifically for that customer
				if self_service.queue_size() < self_service.capacity:
					if not self_service.is_open():
						self_service.open()
					self_service.add_customer(customer)
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
				if opened_lane:
					available_regular_lanes.append(opened_lane)

			# Check if there is an entry in the list to avoid crashes when lanes potentially fill up
			if available_regular_lanes:
				# Initialise the lane with the shortest queue to a default value
				shortest_queue = available_regular_lanes[0]
				for lane in available_regular_lanes:
					# If the current shortest queue is larger than the new queue, the new lane becomes the shortest
					if lane.queue_size() < shortest_queue.queue_size():
						shortest_queue = lane
				shortest_queue.add_customer(customer)
				assigned_customers.append(customer)
				print(f"Customer {customer.id} with {customer.basket_items} basket items {'and a lotto ticket ' if customer.lottery else ''}assigned to {f'Lane {shortest_queue.id}'}\n")
			else:
				# If we have reached this code and the customer can enter self-service, then we know for certain that no
				# other customers will be able to be assigned to lanes during this tick due to every lane being full.
				# If the customer can't enter self-service, then that lane may still be available to other customers that
				# can enter it, so we don't break the loop
				if customer.basket_items < 10:
					break

		# The customers that were assigned to lanes this tick are removed from the lost customers list
		for customer in assigned_customers:
			self.lost_customers.remove(customer)

		# Advances the ticks for each lane and adds any customers that were processed to the total processed count
		for lane in open_lanes:
			lane.increment_ticks()
			self.total_customers_processed += int(lane.customer_processed)

		self.balance_lanes()

		# If the total number of customers outside of lanes exceeds 40, raise an overflow error to say so.
		if len(self.lost_customers) > 40:
			raise OverflowError("Lane saturation has occurred. Unassigned customer count has reached 40")

		# Output the lanes every 30 seconds
		if self.elapsed % 30 == 0:
			self.format_output()

	def introduce_customer(self, customer):
		"""Outputs customer data when added to the simulation"""
		print(f"Customer {customer.id} generated with {customer.basket_items} items{' and a lotto ticket!' if customer.lottery else ''}")
		if customer.basket_items < 10:
			print(f"Time to checkout at self-service: {customer.basket_items * SELF_SERVICE_PROCESS_TIME} seconds")
		print(f"Time to checkout at cashier: {customer.basket_items * REGULAR_PROCESS_TIME} seconds\n")

	def format_output(self):
		"""Formats and outputs the current lane status and customer counts"""

		print(f"Lane status at {self.elapsed // 60}:{f'{self.elapsed % 60}0' if self.elapsed % 60 == 0 else f'{self.elapsed % 60}'}")
		self.output_lanes()

		print("--------------------------------------")
		print(f"Customers currently waiting: {len(self.lost_customers)}")
		print(f"Customers processed so far: {self.total_customers_processed}")
		print(f"Total customers seen: {self.total_customers_seen}")
		print("\n")

	def output_lanes(self):
		"""Part of the format_output method. Made separate to allow the simulation end to use just this bit"""
		for lane in self.lanes:
			data = lane.data()
			print(f"{data['type']:12} (Lane {data['id']}) - {data['customers'] if data['open'] else 'Closed'}")

	def get_open_lanes(self, include_self_service=True):
		"""Returns a list of currently open lanes. Excludes self-service if False given in arguments"""
		open_lanes = []
		for lane in self.lanes:
			if include_self_service & lane.is_open():
				open_lanes.append(lane)
			elif lane.is_open() & lane.is_regular:
				open_lanes.append(lane)

		return open_lanes

	def open_lane(self):
		"""Searches the list for a closed cashier lane, opens it and returns it"""
		for i in range(1, len(self.lanes)):
			lane = self.lanes[i]
			if not lane.is_open():
				lane.open()
				return lane
		return None

	def balance_lanes(self):
		"""Balances the cashier lanes so that every open lane has a queue size
		of no more or less than 1 compared to all other lanes"""
		open_lanes = self.get_open_lanes(False)
		total_customers = 0
		for lane in open_lanes:
			total_customers += lane.queue_size()
		# Taking the average queue size of each open lane and then finding the closest integer both above and below it
		# guarantees that when as balanced as possible each lane will either have a queue size of the integer above or
		# below the average
		average_queue = total_customers / len(open_lanes)
		upper = math.ceil(average_queue)
		lower = math.floor(average_queue)
		for lane in open_lanes:
			for lane_2 in open_lanes:
				while lane.queue_size() > upper:
					if lane_2.queue_size() < lower:
						customer = lane.pop()
						# Resetting time elapsed to prevent issues with how the class determines when to remove an item
						customer.time_elapsed = 0
						lane_2.add_customer(customer)
						print(f"Customer {customer.id} moved from Lane {self.lanes.index(lane) + 1} to {self.lanes.index(lane_2) + 1}")
					else:
						break
