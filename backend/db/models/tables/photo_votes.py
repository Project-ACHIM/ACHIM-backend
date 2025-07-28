from backend.db.models.common import *

class PhotoVote(Base):
    __tablename__ = "photo_votes"

    id = Column(Integer, primary_key=True)
    photo_id = Column(Integer, ForeignKey("uploaded_photos.id"), nullable=False)
    voter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=DateTime.utcnow)

    photo = relationship("UploadedPhoto", back_populates="votes")
    voter = relationship("User")
