import importlib
import uvicorn
import os
import gradio as gr

history_aware_generation = importlib.import_module("4_history_aware_generation")
# from 2_retrieval_pipeline.py import predict_rag
from api import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

class Request(BaseModel):
    prompt : str

class Response(BaseModel):
    response : str

@app.post("/",response_model=Response)
async def predict_api(prompt:Request):
    response = history_aware_generation.ask_question(prompt.prompt)
    return response


demo = gr.ChatInterface(
    fn=history_aware_generation.ask_question,
    textbox=gr.Textbox(
        placeholder="Ask a question", container=False,lines=1,scale=8
    ),
    title="LLM App",
    undo_btn="Delete Previous",
    clear_btn="Clear",
)


app = gr.mount_gradio_app(app, demo, path="/")


if __name__ == "__main__":
    # mounting at the root path
    uvicorn.run(
        app="main:app",
        host=os.getenv("UVICORN_HOST"),  
        port=int(os.getenv("UVICORN_PORT"))
    )