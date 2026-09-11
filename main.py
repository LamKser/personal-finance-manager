from argparse import ArgumentParser
import asyncio

from src.agent import LangGraphAgent
from src.logger import logger

logger()

parser = ArgumentParser(description="Run LangGraph Agent")
parser.add_argument(
    "-p",
    "--prompt",
    type=str,
    required=True,
    help="User prompt to send to the agent",
)

parser.add_argument(
    "-s",
    "--stream",
    action="store_true",
    help="Streaming mode",
)

args = parser.parse_args()

agent = LangGraphAgent()


async def main():
    if not args.stream:
        result = agent.invoke_graph(args.prompt)
        # print("Agent Response:", result)
    else:
        # print("Agent Response: ", end="", flush=True)

        async for chunk in agent.astream(args.prompt):
            print(chunk, end="", flush=True)
        print()


if __name__ == "__main__":
    asyncio.run(main())