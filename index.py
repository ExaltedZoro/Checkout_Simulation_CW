from manager import SimulationManager
import asyncio


async def main():
    manager = SimulationManager()
    await manager.start_sim()


if __name__ == "__main__":
    asyncio.run(main())
