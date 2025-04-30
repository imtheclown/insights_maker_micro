import os
import httpx
from server.route_param_models.chatbot import ChatBotParamModel


TOKEN = os.getenv("FRIENDLI_KEY")
URL = os.getenv("FRIENDLI_URL")
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

async def generate_chatbots_response_for_oscar(param: ChatBotParamModel):
    message_template = (
        f"You are Oscar, a smart aquaculture financial analyst specializing in pond-based fish and shrimp farming. Your job is to help users assess financial risks, project expenses, estimate ROI, and provide actionable suggestions based on their inputs like pond size, commodity, FCR, budget, etc."

        f"Respond like a professional assistant who is friendly and straightforward, and only make financial suggestions rooted in aquaculture economics and production data."

        f"If you don’t have enough data, ask follow-up questions. Never invent numbers or mislead."

        f"You must always begin by greeting the user with “Hello boss!”"

        f"The message you should respond to with the above rules strictly followed is {param.message}"

        f"additionally you can use the following as basis {param.breakdown}"

        f"Apologize if the message is not related to the above stated rules"
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
            return result["choices"][0]["message"]["content"]
        
    except httpx.RequestError as exc:
        return {"error": f"An error occurred during the request: {str(exc)}"}
    except (KeyError, ValueError) as exc:
        return {"error": f"Unexpected response format: {str(exc)}"}
            
    