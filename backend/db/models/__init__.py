# db/models/__init__.py

# 各モデルファイルをimport（使わなくてもimportだけすればOK）
from db.models.user import User
from db.models.auth_providers import AuthProvider
from db.models.sp_record import SPRecord

from db.models.group import Group
from db.models.bp_entry import BPEntry
from db.models.group_member import GroupMember
from db.models.mission_result import MissionResult
from db.models.ranking_result import RankingResult
from db.models.week import Week

# モデルを追加したらここにも追加する！
