import os
import httpx
import re
from server.route_param_models.smart_computation_suggestions import CommodityModel

TOKEN = os.getenv("FRIENDLI_KEY")
URL = os.getenv("FRIENDLI_URL")
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

import json

def format_result(response: str) -> dict:
    try:
        parsed_response = json.loads(response)

        # Validate structure
        formatted_result = {}
        for param, details in parsed_response.items():
            if (
                "insights" in details and
                isinstance(details["insights"], list) and
                "adjusted_value" in details and
                "justification" in details
            ):
                formatted_result[param.lower()] = {
                    "insights": [insight.strip() for insight in details["insights"]],
                    "adjusted_value": details["adjusted_value"].strip(),
                    "justification": details["justification"].strip()
                }
        return formatted_result

    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {str(e)}")


async def generate_smartcalc_suggestions(param: CommodityModel):
    message_template = (
        f"Inputs:\n"
        f"{str(param)}\n\n"
        "You are an aquaculture production optimization expert.\n\n"
        f"The size of the pond is {param.production_setup.area_volume}"
        f"the commodity is {param.commodity}"
        "The context is strictly in the Philippines, use peso as curency"
        "Analyze the provided data to identify specific areas of overspending or inefficiencies.\n"
        "Focus only on parameters that show inefficiency.\n"
        "Do not provide introductions, conclusions, or summaries.\n\n"
        "Your tasks:\n"
        "- Identify only problematic or inefficient parameters.\n"
        "- For each identified parameter:\n"
        "  - Provide a clear, short insight why it is inefficient.\n"
        "  - Suggest an adjusted value to correct the inefficiency.\n"
        "  - Give a brief justification for the adjustment.\n\n"
        "Format (strict):\n\n"
        "```json\n"
        "{\n"
        "  \"[parameter name]\": {\n"
        "    \"insights\": [\n"
        "      \"Insight 1 [why this is an inefficiency or why this should be improved]\",\n"
        "      \"Insight 2 (if necessary)\"\n"
        "    ],\n"
        "    \"adjusted_value\": \"value\",\n"
        "    \"justification [how did you came up with the adjusted value]\": \"reason for adjustment\"\n"
        "  }\n"
        "}\n"
        "```"
    )

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
            response.raise_for_status()
            result = response.json()
            # return format_result(result["choices"][0]["message"]["content"])
            return format_result(result["choices"][0]["message"]["content"])
    except httpx.RequestError as exc:
        return {"error": f"An error occurred during the request: {str(exc)}"}
    except (KeyError, ValueError) as exc:
        return {"error": f"Unexpected response format: {str(exc)}"}
            
    