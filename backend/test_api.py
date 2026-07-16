import asyncio
import httpx

async def main():
    async with httpx.AsyncClient() as client:
        r = await client.post('http://localhost:8000/score', json={'gene':'KMT2D', 'hgvs':'c.123A>G'})
        print(r.status_code)
        print(r.text)

if __name__ == '__main__':
    asyncio.run(main())

