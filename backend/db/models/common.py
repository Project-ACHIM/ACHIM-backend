# db/models/common.py

# SQLAlchemy Core 型や制約
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    TIMESTAMP,
    JSON
)

from sqlalchemy.dialects.postgresql import JSONB

# ORM用（リレーション）
from sqlalchemy.orm import relationship

# サーバー側での日時自動生成
from sqlalchemy.sql import func

# Baseクラス（モデルの継承元）
from backend.db.base import Base

# このファイルからインポート可能なシンボルを明示（import * を防ぐ）
__all__ = [
    "Column",
    "Integer",
    "String",
    "Text",
    "Date",
    "DateTime",
    "ForeignKey",
    "UniqueConstraint",
    "TIMESTAMP",
    "JSON",
    "JSONB",
    "relationship",
    "func",
    "Base"
]
