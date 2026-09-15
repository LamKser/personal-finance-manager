
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse


from src.schema import UserQuery, Response
from src.agent import LangGraphAgent
from src.tools.gg_sheet import get_all_tools
from src.logger import logger

logger()


app = FastAPI()
agent = LangGraphAgent()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/health")
def get_health_check():
    return {"status": "ok"}


@app.get("/tools")
def get_tools():
    return [
        {tool.name: tool.description} for tool in get_all_tools()
    ]


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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    