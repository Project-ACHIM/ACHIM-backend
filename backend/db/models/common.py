# db/models/common.py

# SQLAlchemy Core 型や制約
from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    Text,
    Time,
    Date,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    TIMESTAMP,
    JSON,
    Index,
    BigInteger,
    Float,
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
    "Boolean",
    "Column",
    "Integer",
    "String",
    "Text",
    "Time",
    "Date",
    "DateTime",
    "ForeignKey",
    "UniqueConstraint",
    "TIMESTAMP",
    "JSON",
    "JSONB",
    "relationship",
    "func",
    "Base",
    "Index",
    "BigInteger",
    "Float",
]
