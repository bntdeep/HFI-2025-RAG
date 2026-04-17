import asyncio

from src.rag import configure_logging, print_debug, run_query

configure_logging()  # enables INFO logs from all agent nodes

async def main():
    result = await run_query("compare ranks of Belarus and Austria on personal freedom score")
    print_debug(result)
    print("response:\n", result["response_text"])

asyncio.run(main())