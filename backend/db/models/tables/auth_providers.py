from backend.db.models.common import *

# --- auth_providers ---
class AuthProvider(Base):
    __tablename__ = "auth_providers"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    provider = Column(String(50), nullable=False)
    provider_user_id = Column(String(255), nullable=False)
    email = Column(String(255))
    password_hash = Column(Text)

    user = relationship("User", back_populates="auth_providers")

    __table_args__ = (UniqueConstraint("provider", "provider_user_id"),)