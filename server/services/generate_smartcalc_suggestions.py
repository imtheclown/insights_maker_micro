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

def format_result(text: str) -> dict:
    data = {}
    current_section = None
    lines = text.splitlines()

    for line in lines:
        line = line.strip()
        # Detect section headers
        section_match = re.match(r"\*\*(.*?)\*\*", line)
        if section_match:
            current_section = section_match.group(1).strip()
            data[current_section] = []
        elif current_section:
            if line:  # Skip empty lines
                data[current_section].append(line)
    
    return data

async def generate_smartcalc_suggestions(param: CommodityModel):
    message_template = f"""
        Inputs:
        {str(param)}
        Instructions:
        - Analyze the provided data to identify specific areas of overspending or inefficiencies, with a focus on feed usage and manpower allocation.
        - For each section, follow this format:
        
        **Format for Response**:
        - Label each section as the specific part that has issues (e.g., "Feeds" or "Manpower").
        - Clearly describe the identified issue in this part.
        - Provide the recommended adjustment of value to address the issue, ensuring the recommendations are actionable and easy to implement.

        - Focus on improving survival rate, Feed Conversion Ratio (FCR), and Average Body Weight (ABW), while minimizing costs.
        - Use simple and accessible language to make the response easy to understand.
        - Avoid providing summaries or conclusions; deliver focused content only.
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
            
    