from fastapi import FastAPI, Request
import httpx
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
import re
from pydantic import BaseModel

load_dotenv()

app = FastAPI()

TOKEN = os.getenv("FRIENDLI_KEY")
URL = "https://api.friendli.ai/serverless/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def extract_parameter_insights(response: str) -> dict:
    # Regular expression to extract parameter, value, insight, actions, and products
    pattern = r"\d+\.\s+\*\*(.+?) \((.+?)\)\*\*:\s*-\s+\*\*Insight:\*\*\s*(.+?)\s*-\s+\*\*Actions:\*\*\s*((?:\s*-\s+.+\n?)*)\s*-\s+\*\*Products:\*\*\s*((?:\s*-\s+.+\n?)|None)"

    matches = re.findall(pattern, response)
    result = {}

    for param, value, insight, actions, products in matches:
        action_lines = [line.strip("- ").strip() for line in actions.strip().split("\n") if line.strip()]
        product_lines = [line.strip("- ").strip() for line in products.strip().split("\n") if products.strip() != "None" and line.strip()]

        result[param.lower()] = {
            "value": value,
            "insight": insight,
            "actions": action_lines,
            "products": product_lines if product_lines else []  # Empty array if "None"
        }

    return result

class RestyRouteParam(BaseModel):
    species: str
    temperature:float
    dissolved_oxygen: float
    ph: float
    ammonia: float
    nitrate: float
    salinity: float
    transparency : float


async def get_resty_response(resty_route_param: RestyRouteParam):

    message_template = f"You are an expert in aquaculture. Based on the given water quality readings from a tilapia pond, provide short and specific insights and clear, actionable steps for each parameter. Focus only on what needs to be done. Do not provide general advice or introductions.\n\nFormat:\n\n1. **[Parameter Name] ([Value])**:\n   - **Insight:** [Brief explanation about the value — is it good/bad, and why]\n   - **Actions:**\n     - [Step 1]\n     - [Step 2]\n   - **Products:**\n     - [Product 1] (active ingredient: [active ingredient])\n     - [Product 2] (active ingredient: [active ingredient])\n\nHere are the current water quality parameters:\n\n- Temperature: {resty_route_param.temperature}°C\n- pH: 5.8\n- Dissolved Oxygen: {resty_route_param.dissolved_oxygen} mg/L\n- Ammonia: {resty_route_param.ammonia} ppm\n- Nitrate: 40 ppm\n- Salinity: {resty_route_param.salinity} ppt\n- Transparency: {resty_route_param.transparency} cm and the species is {resty_route_param.species}"

    payload = {
        "model": "meta-llama-3.1-8b-instruct",
        "messages": [{"role": "user", "content": message_template}],
        "min_tokens": 0,
        "max_tokens": 16384,
        "temperature": 1,
        "top_p": 0.8,
        "frequency_penalty": 0,
        "stop": [],
        "stream": False,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(URL, json=payload, headers=HEADERS)
        if(response.status_code != 200):
            print("Error: Status code", response.status_code)
            print("Response text:", response.text)
            return {"error": "Failed to get valid response."}
        
        result = response.json()
        return extract_parameter_insights(result["choices"][0]["message"]["content"])
    

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    user_message = body.get("message", "")
    if not user_message:
        return {"error": "Message is required"}

    response_text = await get_resty_response(user_message)
    return JSONResponse(content={"response": response_text})