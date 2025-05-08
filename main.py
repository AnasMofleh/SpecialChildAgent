from semantic_kernel.contents import (
    FunctionCallContent,
    FunctionResultContent,
    StreamingTextContent,
)
from semantic_kernel.agents import ChatCompletionAgent, ChatHistoryAgentThread
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from openai import AsyncOpenAI


from WebsiteReaderPlugin import WebsiteReaderPlugin
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
import uvicorn
import json
import html
import os


load_dotenv()

# Emoji icons for accessibility and readability
ICONS = {"user": "👤", "agent": "🤖", "function": "🛠️", "result": "📄"}

# Dummy imports: Replace with your actual imports
# from your_agent import agent, ChatHistoryAgentThread, FunctionCallContent, FunctionResultContent, StreamingTextContent

app = FastAPI()
agent = None  # Define agent as a global variable
# Serve static files (like index.html)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def root():
    return FileResponse("static/index.html")


@app.on_event("startup")
async def startup():
    global agent  # Declare agent as global to modify it
    endpoint = "https://models.inference.ai.azure.com/"
    # endpoint = "https://models.github.ai/inference"
    model = "gpt-4o-mini"  # "openai/gpt-4.1"
    embeddings_model = "text-embedding-3-large"  # "text-embedding-3-small"
    token = os.environ["OPENAI_API_KEY"]
    client = AsyncOpenAI(base_url=endpoint, api_key=token)

    #   Create an AI Service that will be used by the `ChatCompletionAgent`
    chat_completion_service = OpenAIChatCompletion(
        ai_model_id=model, async_client=client
    )

    AGENT_INSTRUCTIONS = """
You are a helpful AI Agent that can assist users in finding relevant information and resources regarding children with special needs from the "MittSpeciellaBarn" website.
Important: When users specify a topic or query, always focus on providing information related to that topic from the website. 
Only suggest general resources when an answer is not relevant from the website. prioritize user preferences. 
When the conversation begins, introduce yourself with this message:
"Hello! I'm your Mitt Speciella Barn assistant. I can help you find information resources and activites related to support for children and individuals with disabilities. Here are some things you can ask me:
1. How to apply for financial support for children with disabilities.
2. Information about specific services or activities.
3. Details about community support and resources.
What can I help you with today?"
Always  
Answer in the same langague as the question and provide a link (if exists) to the relevant page on the website at the end of the response.
If they mention a specific topic like "financial support" or "community activities," focus your assistance on that topic rather than suggesting unrelated resources. 
"""

    wcp = WebsiteReaderPlugin(client=client, embeddings_model=embeddings_model)
    await wcp.read_index(filename="urlEmbeddings.csv")

    agent = ChatCompletionAgent(
        service=chat_completion_service,
        plugins=[wcp],
        name="WebsiteAgent",
        instructions=AGENT_INSTRUCTIONS,
    )

    return agent


class ChatRequest(BaseModel):
    user_inputs: List[str]


async def chat(request: ChatRequest):
    global agent  # Access the global agent variable


# You could use a global or session-bound thread (for now, just keep in memory)
active_thread: ChatHistoryAgentThread | None = None


@app.post("/chat")
async def chat(request: ChatRequest):
    global active_thread  # Keeps thread memory across function calls (in-memory only)
    user_inputs = request.user_inputs
    html_blocks = []

    for user_input in user_inputs:
        escaped_input = html.escape(user_input)
        html_output = ""

        agent_name = None
        full_response: list[str] = []
        function_calls: list[str] = []
        current_function_name = None
        argument_buffer = ""

        async for response in agent.invoke_stream(
            messages=user_input, thread=active_thread
        ):
            active_thread = response.thread  # Update thread each time
            agent_name = response.name
            content_items = list(response.items)

            for item in content_items:
                if isinstance(item, FunctionCallContent):
                    if item.function_name:
                        current_function_name = item.function_name
                    if isinstance(item.arguments, str):
                        argument_buffer += item.arguments

                elif isinstance(item, FunctionResultContent):
                    if current_function_name:
                        formatted_args = argument_buffer.strip()
                        try:
                            parsed_args = json.loads(formatted_args)
                            formatted_args = json.dumps(parsed_args, indent=2)
                        except Exception:
                            pass
                        function_calls.append(
                            f"<div><strong>{ICONS['function']} Calling:</strong> {current_function_name}"
                            f"<pre style='background:#eee; padding:0.5em; border-radius:5px;'>{html.escape(formatted_args)}</pre></div>"
                        )
                        current_function_name = None
                        argument_buffer = ""

                    function_calls.append(
                        f"<div><strong>{ICONS['result']} Result:</strong><pre style='background:#f0f0f0; padding:0.5em; border-radius:5px;'>{html.escape(str(item.result))}</pre></div>"
                    )

                elif isinstance(item, StreamingTextContent) and item.text:
                    full_response.append(item.text)

        # Collapsible function call section
        if function_calls:
            html_output += f"""
            <details style="margin:1em 0;">
                <summary style="cursor:pointer; font-weight:bold; color:#336699;">
                    {ICONS['function']} Function Calls (click to expand)
                </summary>
                <div style="margin-top:0.5em; font-size:0.95em;">
                    {"<hr>".join(function_calls)}
                </div>
            </details>
            """

        html_output += f"""
        <section style="margin:1em 0;">
            <div style="font-weight:bold;">{ICONS['agent']} {html.escape(agent_name or 'Assistant')}:</div>
            <div style="margin-left:1em; white-space:pre-wrap;">{html.escape(''.join(full_response).strip())}</div>
        </section>
        <hr style="border:none; border-top:1px solid #ccc; margin:2em 0;">
        """

        html_blocks.append(html_output)

    return {"html": "\n".join(html_blocks)}


# For local testing
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
