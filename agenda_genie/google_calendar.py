"""
Googleカレンダーとの連携を担当するモジュール。

CalendarEventオブジェクトを受け取り、Google Calendar APIを呼び出して
カレンダーへのイベント登録・操作を行います。
"""

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .schemas import CalendarEvent

# Google Calendar APIのスコープを定義
SCOPES = ["https://www.googleapis.com/auth/calendar"]


class GoogleCalendarManager:
    """
    Googleカレンダーの操作を管理するクラス。
    """

    def __init__(self, credentials_file="credentials.json", token_file="token.json"):
        """
        認証情報を初期化し、Google Calendar APIへの接続を準備します。
        """
        creds = None
        # token.jsonが存在すれば、有効な認証情報を読み込む
        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)

        # 認証情報が無効または存在しない場合、再認証を行う
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # credentials.jsonから認証フローを作成
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file, SCOPES
                )

                # ユーザーにブラウザでの認証を要求
                creds = flow.run_local_server(port=0)

            with open(token_file, "w") as token:
                token.write(creds.to_json())

        self.service = build("calendar", "v3", credentials=creds)

    def create_event(self, event: CalendarEvent) -> None:
        """
        新しいイベントをGoogleカレンダーに登録します。

        Args:
            event: 登録するイベント情報を持つCalendarEventオブジェクト。
        """
        # CalendarEventオブジェクトをGoogle Calendar APIのフォーマットに変換
        event_body = {
            "summary": event.title,
            "description": event.description,
            "start": {
                "dateTime": event.start_time.isoformat(),
                "timeZone": "Asia/Tokyo",  # 必要に応じて変更
            },
            "end": {
                "dateTime": event.end_time.isoformat(),
                "timeZone": "Asia/Tokyo",  # 必要に応じて変更
            },
        }

        try:
            # 'primary'はメインのカレンダーIDを指す
            created_event = (
                self.service.events()
                .insert(calendarId="primary", body=event_body)
                .execute()
            )
            print(f"Event created: {created_event.get('htmlLink')}")
        except HttpError as error:
            print(f"An error occurred: {error}")
