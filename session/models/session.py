from sqlalchemy import Column, Integer, String, DateTime, Float, UUID
from datetime import datetime
from sqlalchemy.orm import relationship
from config.base_class import Base

class Session(Base):
    __tablename__ = 'session'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(UUID, index=True, unique=True, nullable=False)
    
    ip_address = Column(String(45))  # IPv6 поддержка
    referer = Column(String(2048))
    
    utm_source = Column(String(255))
    utm_medium = Column(String(255))
    utm_campaign = Column(String(255))
    utm_term = Column(String(255))
    utm_content = Column(String(255))

    time_spent = Column(Float)  # В секундах, можно в минутах, как нужно
    user_agent = Column(String(512))
    screen_resolution = Column(String(20))  # Например, '1920x1080'
    browser_language = Column(String(50))

    created_at = Column(DateTime, default=datetime.utcnow)
    order_infos = relationship("OrderInfo", back_populates="session")