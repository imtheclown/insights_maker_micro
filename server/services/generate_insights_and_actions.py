import os
import httpx
import re
from server.route_param_models.generate_insights_and_actions import GenerateInsightActionsParams

TOKEN = os.getenv("FRIENDLI_KEY")
URL = os.getenv("FRIENDLI_URL")
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def extract_parameter_insights(response: str) -> dict:
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
            "products": product_lines if product_lines else []
        }
    return result

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
        "    \"actions\": [\n"
        "      \"Action step 1\",\n"
        "      \"Action step 2\"\n"
        "    ],\n"
        "    \"products\": [\n"
        "      \"chemical1\",\n"
        "      \"chemical2\"\n"
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
            response = await client.post(URL, json=payload, headers=HEADERS, timeout=10)
            response.raise_for_status()
            result = response.json()
            return extract_parameter_insights(result["choices"][0]["message"]["content"])
    except httpx.RequestError as exc:
        error_detail = getattr(exc.response, 'text', str(exc))
        return {"error": f"Request error: {error_detail}"}
    except (KeyError, ValueError) as exc:
        return {"error": f"Unexpected response format: {str(exc)}"}
