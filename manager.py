from random import randint
from time import perf_counter
import asyncio

from lanes import RegularLane, SelfServiceLane
from customer import Customer


class SimulationManager:

	def __init__(self):

		self.running = False
		self.start_time = None
		self.duration = 60.0
		self.elapsed = 0

		self.total_customers_seen = 0
		self.total_customers_processed = 0

		self.lanes = [
			RegularLane(),
			RegularLane(),
			RegularLane(),
			RegularLane(),
			RegularLane(True),
			SelfServiceLane(True)
		]
		self.lost_customers = []

	async def start_sim(self):
		self.running = True
		self.start_time = perf_counter()
		while self.elapsed != self.duration:
			await self.sim_loop()
		print("Simulation ended")
		print(f"Total customers seen: {self.total_customers_seen}")
		print(f"Total customers processed: {self.total_customers_processed}")

	async def sim_loop(self):
		# Use this to enable an actual timer-thing
		# await asyncio.sleep(1.0)
		self.elapsed += 1.0

		generated_customers = []

		if self.elapsed == 1.0:
			generated_customers = self.gen_customers(10)
		elif randint(1, 5) == 5:
			generated_customers = self.gen_customers()

		self.lost_customers += generated_customers
		self.total_customers_seen += len(generated_customers)

		for c in self.lost_customers:
			lane_result = self.assign_customer(c)
			if lane_result:
				lane_result.customers.append(c)
				self.lost_customers.remove(c)
			else:
				if c.basket_items < 10:
					break

		open_lanes = filter(lambda x: x.open is True, self.lanes)
		for lane in open_lanes:
			lane.increment_ticks()

		self.format_output()

	def format_output(self):
		customers_processed = 0

		for lane in self.lanes:
			data = lane.data()
			customers_processed += int(data["customer_processed"])
			print(f"Lane {data['id']} ({data['type']}) - {data['customers'] if data['open'] else 'Closed'}")

		self.total_customers_processed += customers_processed
		print("--------------------------------------")
		print(f"Tick {self.elapsed} / {self.duration}")
		print(f"Customers waiting this tick: {len(self.lost_customers)}")
		print(f"Customers processed this tick: {customers_processed}")
		print("\n")

	def gen_customers(self, max_num=40):
		new_customers = randint(0, min(max_num, 40 - len(self.lost_customers)))
		return [Customer() for i in range(0, new_customers)]

	def find_lane(self, is_open=True, include_self_service=True, include_regular=True):
		found = False
		counter = 0
		while not found and counter <= len(self.lanes)-1:
			lane = self.lanes[counter]
			if lane.open == is_open and len(lane.customers) < lane.capacity and ((include_self_service and include_regular) or (lane.is_regular == include_regular) or (lane.is_regular != include_self_service)):
				found = True
			else:
				counter += 1

		if found:
			return self.lanes[counter]
		else:
			return None

	def assign_customer(self, customer):
		use_self_service = customer.basket_items < 10
		free_lane = self.find_lane(include_self_service=use_self_service)
		if free_lane:
			return free_lane
		else:
			lane_to_open = self.find_lane(is_open=False, include_self_service=use_self_service)
			if lane_to_open:
				lane_to_open.open = True
				return lane_to_open
			else:
				return None
