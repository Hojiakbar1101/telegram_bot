from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database.models import Base

class View(Base):
    __tablename__ = "views"

    id = Column(Integer, primary_key=True)
    viewer_id = Column(Integer, ForeignKey("users.id"))
    viewed_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)

    viewer = relationship("User", foreign_keys=[viewer_id])
    viewed = relationship("User", foreign_keys=[viewed_id])
