# db/models/__init__.py

# 各モデルファイルをimport（使わなくてもimportだけすればOK）
from backend.db.models.tables.users import User
from backend.db.models.tables.auth_providers import AuthProvider
from backend.db.models.tables.sp_records import SPRecord
from backend.db.models.tables.groups import Group
from backend.db.models.tables.bp_entries import BPEntry
from backend.db.models.tables.group_members import GroupMember
from backend.db.models.tables.mission_results import MissionResult
from backend.db.models.tables.ranking_results import RankingResult
from backend.db.models.tables.weeks import Week
from backend.db.models.tables.exchanges import Exchange
from backend.db.models.tables.discount_tickets import DiscountTicket

# モデルを追加したらここにも追加する！
