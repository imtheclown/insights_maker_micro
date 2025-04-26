from pydantic import BaseModel

class GenerateInsightActionsParams(BaseModel):
    stocking_density: float
    fcr: float
    survival_rate: float
    average_weight :float
    species: str
    dissolved_oxygen: float
    temperature: float
    ammonia: float
    nitrate: float
    ph: float
    salinity: float
    turbidity: float
    culture_age_in_days: int



