
from pydantic import BaseModel

class ProductionSetup(BaseModel):
    area_volume: float
    days_of_culture: float
    population_stocked: float
    survival_rate: float
    density: float
    abw: float
    biomass: float
    tons_per_hectare: float
    fcr: float

class DirectCosts(BaseModel):
    harvest_expense: float
    pond_prep: float
    fry_fingerlings: float
    feeds: float
    inputs: float
    laboratory_charges: float
    pumping_cost: float
    power_cost: float

class OverheadCosts(BaseModel):
    manpower_cost: float
    meals: float
    office_supplies: float
    miscellaneous: float
    ptt: float
    water_expense: float
    fuel_sv: float
    security_expense: float
    rent_expense: float
    other_expenses: float
    repairs_maintenance: float
    depreciation: float

class CommodityModel(BaseModel):
    commodity: str
    pond_size_sqm: float
    total_budget_php: float
    production_setup: ProductionSetup
    direct_costs: DirectCosts
    overhead_costs: OverheadCosts