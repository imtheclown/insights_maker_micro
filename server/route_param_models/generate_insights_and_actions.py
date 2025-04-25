from pydantic import BaseModel

class GenerateInsightActionsParams(BaseModel):
    species: str
    temperature: float
    dissolved_oxygen: float
    ph: float
    ammonia: float
    nitrate: float
    salinity: float
    transparency: float