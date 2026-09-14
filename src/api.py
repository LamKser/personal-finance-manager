
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.responses import StreamingResponse


from src.schema import UserQuery, Response
from src.agent import LangGraphAgent
from src.logger import logger

logger()


app = FastAPI()
agent = LangGraphAgent()


@app.post("/chat/stream")
async def stream(user: UserQuery):
    async def generate():
        async for chunk in agent.astream(user.prompt):
            response = Response(
                        message=chunk,
                        timestamp=datetime.now(timezone.utc),
                    )
            yield response.model_dump_json() + "\n"
    return StreamingResponse(generate(), media_type="application/json")


@app.post("/chat")
async def chat(user: UserQuery):
    result = agent.invoke_graph(user.prompt)
    return Response(
                message=result["messages"][-1].content,
                timestamp=datetime.now(timezone.utc),
            )
