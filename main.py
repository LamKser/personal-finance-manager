from argparse import ArgumentParser

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

args = parser.parse_args()

agent = LangGraphAgent()

result = agent.invoke_graph(args.prompt)
