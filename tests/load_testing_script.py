import asyncio
import aiohttp
import time

# Configuration for load test
CONCURRENT_USERS = 100
TOTAL_REQUESTS = 1000
TARGET_URL = 'http://localhost:8000/api/endpoint'

async def fetch(session, url):
    async with session.get(url) as response:
        await response.text()
        return response.status

async def bound_fetch(sem, session, url):
    async with sem:
        return await fetch(session, url)

async def run_load_test():
    sem = asyncio.Semaphore(CONCURRENT_USERS)
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(TOTAL_REQUESTS):
            task = asyncio.create_task(bound_fetch(sem, session, TARGET_URL))
            tasks.append(task)
        responses = await asyncio.gather(*tasks)
        return responses

if __name__ == '__main__':
    start_time = time.time()
    responses = asyncio.run(run_load_test())
    end_time = time.time()

    success = sum(1 for r in responses if 200 <= r < 300)
    failed = len(responses) - success

    print(f'Total requests: {len(responses)}')
    print(f'Successful responses: {success}')
    print(f'Failed responses: {failed}')
    print(f'Total time taken: {end_time - start_time:.2f} seconds')
    print(f'Average requests per second: {len(responses) / (end_time - start_time):.2f}')
