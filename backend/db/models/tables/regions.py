from backend.db.models.common import *

class Region(Base):
    __tablename__ = "regions"

    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False, unique=True)  # 例：東京都
    code = Column(String(5), nullable=False, unique=True)   # 例：13
    area_group = Column(String(20), nullable=True)          # 例: 関東、東日本

    users = relationship("User", back_populates="region")