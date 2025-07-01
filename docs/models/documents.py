from sqlalchemy import Column, String, Text, Boolean, DateTime, func, Integer
from config.base_class import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, nullable=False)  # ключ для URL: 'privacy-policy'
    title = Column(String(255), nullable=False)              # Заголовок документа
    content = Column(Text, nullable=False)                   # Содержимое (можно хранить HTML/Markdown)
    is_active = Column(Boolean, default=True)                # Флаг активности
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())