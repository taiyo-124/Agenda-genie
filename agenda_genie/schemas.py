"""
アプリケーション内で使用されるデータ構造（スキーマ）を定義します。

このモジュールで定義されたクラスは、生成AIが自然言語から情報を抽出し、
Google Calendar APIに渡すための一貫したデータ形式を提供します。
"""

from dataclasses import dataclass
from datetime import datetime


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
