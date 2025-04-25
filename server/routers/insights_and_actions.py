from fastapi import APIRouter, Request
from pydantic import ValidationError
from fastapi.responses import JSONResponse
from server.route_param_models.generate_insights_and_actions import GenerateInsightActionsParams
from server.services.generate_insights_and_actions import generate_insights_and_actions as service
router = APIRouter()

@router.post("/insights_and_actions/")
async def generate_insights_and_actions(request: Request):
    try:
        body = await request.json()
        params = GenerateInsightActionsParams(**body)
        response = await service(params)
        return response
    except ValidationError as e:
        return JSONResponse(content={"error": f"Invalid input: {e}"}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"error": f"An unexpected error occurred: {str(e)}"}, status_code=500)