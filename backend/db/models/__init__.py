# db/models/__init__.py

# 各モデルファイルをimport（使わなくてもimportだけすればOK）
from backend.db.models.tables.regions import Region #追記
from backend.db.models.tables.users import User
from backend.db.models.tables.groups import Group
from backend.db.models.tables.auth_providers import AuthProvider
from backend.db.models.tables.sp_records import SPRecord
from backend.db.models.tables.group_members import GroupMember
from backend.db.models.tables.mission_results import MissionResult
from backend.db.models.tables.ranking_results import RankingResult
from backend.db.models.tables.weeks import Week
from backend.db.models.tables.exchanges import Exchange
from backend.db.models.tables.discount_tickets import DiscountTicket
from backend.db.models.tables.bp_entries import BpEntry
from backend.db.models.tables.user_week_preference import UserWeekPreference
from backend.db.models.tables.mvp_awards import MVPAward

