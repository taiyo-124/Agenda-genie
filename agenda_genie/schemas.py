"""
アプリケーション内で使用されるデータ構造（スキーマ）を定義します。

このモジュールで定義されたクラスは、生成AIが自然言語から情報を抽出し、
Google Calendar APIに渡すための一貫したデータ形式を提供します。
"""

from dataclasses import dataclass
from datetime import datetime

from enum import Enum
from typing import Optional


@dataclass
class CalendarEvent:
    """
    Googleカレンダーのイベント情報を表現するデータクラス。

    Attributes:
        title: イベントのタイトル。
        start_time: イベントの開始日時。
        end_time: イベントの終了日時。
        description: イベントの詳細やメモ。
    """

    title: str
    start_time: datetime
    end_time: datetime
    description: str | None = None  # 説明は任意項目とする

class ActionType(Enum):
    """ユーザーが要求している操作の種類"""
    CREATE = "create" # 作成
    DELETE = "delete" # 削除
    READ = "read" # 読み取り・確認
    TALK = "talk" # 会話

class ParsedResult:
    """AIによる自然言語解析の結果を格納するクラス"""
    def __init__(self, action: ActionType, event: Optional[CalendarEvent] = None, original_text: str = ""):
        self.action = action
        self.event = event
        self.original_text = original_text
        