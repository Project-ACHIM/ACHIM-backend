from backend.db.models.common import *

# --- users ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(10))
    profile_image = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 追加項目
    birth_date = Column(Date)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False)
    wake_up_time = Column(Time)
    notification_enabled = Column(Boolean, default=True)



    # relation
    auth_providers = relationship("AuthProvider", back_populates="user")
    sp_records = relationship("SPRecord", back_populates="user")
    bp_entries = relationship("BpEntry", back_populates="user")
    group_memberships = relationship("GroupMember", back_populates="user")
    mission_results = relationship("MissionResult", back_populates="user")
    ranking_results = relationship("RankingResult", back_populates="user", cascade="all, delete-orphan")
    week_preferences = relationship("UserWeekPreference", back_populates="user", cascade="all, delete-orphan")
    region = relationship("Region", back_populates="users")

