from fastapi import APIRouter

from .products.router import router as product
from .categories.router import router as categories
from .manufacturers.router import router as manufacturers
from .collections.router import router as collections
from .seasons.router import router as seasons
from .sexes.router import router as sexes
from .materials.router import router as materials
from .measure_units.router import router as measure_units
from .colors.router import router as colors
from .filters.router import router as filters

routers = APIRouter()

routers.include_router(product)
routers.include_router(filters)
routers.include_router(categories)
routers.include_router(manufacturers)
routers.include_router(collections)
routers.include_router(seasons)
routers.include_router(sexes)
routers.include_router(materials)
routers.include_router(measure_units)
routers.include_router(colors)