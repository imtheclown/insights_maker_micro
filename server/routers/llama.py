from fastapi import APIRouter, Request 
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from server.route_param_models.smart_computation_suggestions import CommodityModel
from server.route_param_models.generate_insights_and_actions import GenerateInsightActionsParams

router = APIRouter()

from server.services.generate_insights_and_actions import generate_insights_and_actions as generate_insights_actions_service
@router.post("/insights_and_actions/")
async def generate_insights_and_actions(request: Request):
    try:
        body = await request.json()
        params = GenerateInsightActionsParams(**body)
        response = await generate_insights_actions_service(params)
        return response
    except ValidationError as e:
        return JSONResponse(content={"error": f"Invalid input: {e}"}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"error": f"An unexpected error occurred: {str(e)}"}, status_code=500)

from server.services.generate_smartcalc_suggestions import generate_smartcalc_suggestions as generate_calculation_suggestions_service
@router.post("/smart_calc_suggestions/")
async def generate_calculation_suggestions(request: Request):
    try:
        body = await request.json()
        params = CommodityModel(**body)
        result = await generate_calculation_suggestions_service(params)
        return result
    except ValidationError as e:
        return JSONResponse(content={"error": f"Invalid input: {e}"}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"error": f"An unexpected error occurred: {str(e)}"}, status_code=500)