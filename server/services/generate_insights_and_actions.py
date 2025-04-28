import os
import httpx
import json
from fastapi import HTTPException
from server.route_param_models.generate_insights_and_actions import GenerateInsightActionsParams

TOKEN = os.getenv("FRIENDLI_KEY")
URL = os.getenv("FRIENDLI_URL")
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def convert_to_json(response: str) -> dict:
    # If response is a stringified JSON, parse it directly
    parsed_response = json.loads(response)
    return parsed_response

async def generate_insights_and_actions(param: GenerateInsightActionsParams):
    message_template = (
        "You are an expert in aquaculture.\n\n"
        "With the following data reading on a pond:\n"
        f"stocking density: {param.stocking_density} commodity/meter cube\n"
        f"fcr: {param.fcr}\n"
        f"survival rate: {param.survival_rate}\n"
        f"average weight: {param.average_weight} grams\n"
        f"dissolved oxygen: {param.dissolved_oxygen} mg/L\n"
        f"temperature: {param.temperature} celsius\n"
        f"ammonia: {param.ammonia} mg/L\n"
        f"nitrate: {param.nitrate} mg/L\n"
        f"pH: {param.ph}\n"
        f"salinity: {param.salinity} ppt\n"
        f"turbidity: {param.turbidity} NTU\n"
        f"commodity: {param.species}\n"
        f"culture age in days: {param.culture_age_in_days}\n\n"
        "Your tasks:\n"
        "- do not provide introduction or conclusion"
        "- Identify parameters that may negatively affect the commodity.\n"
        "- Consider the commodity and the culture age for biological-based parameters like average weight, FCR, and survival rate.\n"
        "- For each problematic parameter:\n"
        "  - Provide clear, actionable insights.\n"
        "  - List specific active ingredients or chemicals (e.g., \"sodium silicate\", \"enzyme complex\", \"nitrate-reducing bacteria\").\n"
        "  - If no active ingredient is provided or needed, return an empty array [].\n\n"
        "Format (strict):\n\n"
        "```json\n"
        "{\n"
        "  \"[parameter name]\": {\n"
        "   \"insights\": [\n"
        "      \"insight 1\",\n"
        "      \"insight 2 [if necessary]\"\n"
        "    ],\n"
        "    \"actions\": [\n"
        "      \"Action step 1\",\n"
        "      \"Action step 2 [if necessary]\"\n"
        "    ],\n"
        "    \"products\": [\n"
        "      \"product type 1 [feed, aerator, medicine, etc] ([active ingredient if product type is chemical])\",\n"
        "      \"product type 2 [if necessary] [feed, aerator, medicine, etc] ([active ingredient if product type is chemical])\"\n"
        "    ]\n"
        "  }\n"
        "}\n"
        "```"
    )

    payload = {
        "model": "meta-llama-3.1-8b-instruct",
        "messages": [{"role": "user", "content": message_template}],
        "min_tokens": 0,
        "max_tokens": 4096,  # safer upper limit
        "temperature": 1,
        "top_p": 0.8,
        "frequency_penalty": 0,
        "stop": [],
        "stream": False,
    }

    try:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(URL, json=payload, headers=HEADERS, timeout=10)
                response.raise_for_status()
                result = response.json()
                result = convert_to_json(result["choices"][0]["message"]["content"])
                return result
            except Exception as e:
                print(e)
                raise HTTPException(
                status_code=400,
                detail="Invalid request parameters."
    )

    except httpx.RequestError as exc:
        error_detail = getattr(exc.response, 'text', str(exc))
        return {"error": f"Request error: {error_detail}"}
    except (KeyError, ValueError) as exc:
        return {"error": f"Unexpected response format: {str(exc)}"}
