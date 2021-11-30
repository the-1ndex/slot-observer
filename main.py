import asyncio
import os

import httpx
import statsd

from datetime import datetime

client = statsd.StatsClient(os.environ.get('STATSD_HOST', 'localhost'))
endpoints = [('index', 'https://demo.theindex.io'),
             ('ssc', 'https://ssc-dao.genesysgo.net'),
             ('triton', 'https://api.mainnet-beta.solana.com'),
             ('serum', 'https://solana-api.projectserum.com')]

http_client = httpx.AsyncClient()


async def main():
    while True:
        results = []

        now = datetime.now()
        for endpoint, url in endpoints:
            result = http_client.post(url, json={"jsonrpc": "2.0", "id": 1, "method": "getSlot"}, timeout=1)
            results.append((result, endpoint))
        print(now.strftime("%m/%d/%Y, %H:%M:%S"))
        for result, endpoint in results:
            try:
                result = await result
                slot = result.json()['result']
                print(f'{endpoint}\t{slot}')
                client.gauge(f'validator.{endpoint}.slot.processed', slot)
            except Exception as e:
                print(e)
        await asyncio.sleep(10 - (datetime.now() - now).total_seconds())


if __name__ == '__main__':
    asyncio.run(main())
