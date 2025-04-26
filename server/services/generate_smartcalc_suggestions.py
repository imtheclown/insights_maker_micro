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

def format_result(response: str) -> dict:
    # Regular expression to match the pattern for each section
    pattern = r"\*\*(.+?)\*\*:\s*-\s+\*\*Insight:\*\*\s*(.+?)\s*-\s+\*\*Adjusted value:\*\*\s*(.+?)\s*-\s+\*\*Justification:\*\*\s*(.+?)"
    matches = re.findall(pattern, response)
    result = {}

    for section, insight, adjusted_value, justification in matches:
        # Convert section names to lowercase and use them as keys
        result[section.lower()] = {
            "insight": insight.strip(),
            "adjusted_value": adjusted_value.strip(),
            "justification": justification.strip()
        }

    return result

async def generate_smartcalc_suggestions(param: CommodityModel):
    message_template = f"""
        Inputs:
        {str(param)}
        Analyze the provided data to identify specific areas of overspending or inefficiencies
        Response should only contain values with inefficiencies
        Format for Response:  
        **[Affected parameter]**:\n
        - **Insight:** [Brief explanation about the value — is it good/bad, and why]\n
        - **Adjusted value:** value
        - **Justification:** justification for the adjusted value
        Notes:  
        - Keep the analysis sharply focused on individual sections; avoid overarching summaries or conclusions.  
        """

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
            return format_result(result["choices"][0]["message"]["content"])
    except httpx.RequestError as exc:
        return {"error": f"An error occurred during the request: {str(exc)}"}
    except (KeyError, ValueError) as exc:
        return {"error": f"Unexpected response format: {str(exc)}"}
            
    