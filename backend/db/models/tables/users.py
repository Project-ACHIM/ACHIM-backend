from backend.db.models.common import *

# --- users ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(10))
    profile_image = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # relation
    auth_providers = relationship("AuthProvider", back_populates="user")
    sp_records = relationship("SPRecord", back_populates="user")
    bp_entries = relationship("BpEntry", back_populates="user")
    group_memberships = relationship("GroupMember", back_populates="user")
    mission_results = relationship("MissionResult", back_populates="user")
    ranking_results = relationship("RankingResult", back_populates="user", cascade="all, delete-orphan")