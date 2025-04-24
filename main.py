from fastapi import FastAPI, Request
import httpx
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
import re
from pydantic import BaseModel, ValidationError

load_dotenv()

app = FastAPI()

TOKEN = os.getenv("FRIENDLI_KEY")
URL = os.getenv("FRIENDLI_URL")
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Data model for parameters
class RestyRouteParam(BaseModel):
    species: str
    temperature: float
    dissolved_oxygen: float
    ph: float
    ammonia: float
    nitrate: float
    salinity: float
    transparency: float

# Function to extract parameter insights using regex
def extract_parameter_insights(response: str) -> dict:
    # Regular expression to extract details
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

# Function to get response from external service
async def get_resty_response(resty_route_param: RestyRouteParam):
    # Message template for the external service
    message_template = (
        f"You are an expert in aquaculture. Based on the given water quality readings from a tilapia pond, "
        f"provide short and specific insights and clear actions to address the issue . Focus only on what needs to be done."
        f"product suggestions must be strictly tied to aquaculture"
        f"Do not provide general advice or introductions.\n\nFormat:\n\n"
        f"1. **[Parameter Name] ([Value])**:\n"
        f"   - **Insight:** [Brief explanation about the value — is it good/bad, and why]\n"
        f"   - **Actions:** [What to do to fix the issue]\n"
        f"     - [Step 1]\n"
        f"     - [Step 2]\n"
        f"   - **Products:**\n"
        f"     - [Product type] (active ingredient: [active ingredient])\n"
        f"     - [Product type] (active ingredient: [active ingredient])\n\n"
        f"Here are the current water quality parameters:\n\n"
        f"- Species: {resty_route_param.species}\n"
        f"- Temperature: {resty_route_param.temperature}°C\n"
        f"- Dissolved Oxygen: {resty_route_param.dissolved_oxygen} mg/L\n"
        f"- pH: {resty_route_param.ph}\n"
        f"- Ammonia: {resty_route_param.ammonia} ppm\n"
        f"- Nitrate: {resty_route_param.nitrate} ppm\n"
        f"- Salinity: {resty_route_param.salinity} ppt\n"
        f"- Transparency: {resty_route_param.transparency} cm"
    )

    # Payload for the external request
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

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(URL, json=payload, headers=HEADERS, timeout=10)
            response.raise_for_status()  # Raise exception for HTTP errors
            result = response.json()
            return extract_parameter_insights(result["choices"][0]["message"]["content"])
    except httpx.RequestError as exc:
        return {"error": f"An error occurred during the request: {str(exc)}"}
    except (KeyError, ValueError) as exc:
        return {"error": f"Unexpected response format: {str(exc)}"}

# API endpoint
@app.post("/resty/insights")
async def chat(request: Request):
    try:
        body = await request.json()
        params = RestyRouteParam(**body)  # Validate and parse the input
        response_text = await get_resty_response(params)
        return JSONResponse(content={"response": response_text})
    except ValidationError as e:
        return JSONResponse(content={"error": f"Invalid input: {e}"}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"error": f"An unexpected error occurred: {str(e)}"}, status_code=500)