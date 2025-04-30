from pydantic import BaseModel
from server.route_param_models.smart_computation_suggestions import CommodityModel
class ChatBotParamModel(BaseModel):
    message: str
    breakdown: CommodityModel