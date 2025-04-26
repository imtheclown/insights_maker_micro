from fastapi import FastAPI
from dotenv import load_dotenv
import re

load_dotenv()

app = FastAPI()

# import routers
from server.routers.llama import router as generate_router

app.include_router(generate_router, prefix="/generate")

@app.get("/")
def read_root():
    return {"message": "This is api generates insights and actions on water quality parameters"}
