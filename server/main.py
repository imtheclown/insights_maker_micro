from fastapi import FastAPI
from dotenv import load_dotenv
import re

load_dotenv()

app = FastAPI()

# import routers
from server.routers.insights_and_actions import router as insights_actions_routers

app.include_router(insights_actions_routers, prefix="/generate")

@app.get("/")
def read_root():
    return {"message": "This is api generates insights and actions on water quality parameters"}
