from sqlalchemy import Column, Integer, String
from config.base_class import Base

class CarouselImage(Base):
    __tablename__ = "carousel_images"

    id = Column(Integer, primary_key=True, autoincrement=True)
    src = Column(String, nullable=False)   # URL изображения
    href = Column(String, nullable=False)  # Ссылка при клике