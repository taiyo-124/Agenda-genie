"""
Googleカレンダーとの連携を担当するモジュール。

CalendarEventオブジェクトを受け取り、Google Calendar APIを呼び出して
カレンダーへのイベント登録・操作を行います。
"""
import datetime
import os.path
from typing import List, Dict, Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .schemas import CalendarEvent

# Google Calendar APIのスコープを定義
# 読み書き両方の権限を与える
SCOPES = ['https://www.googleapis.com/auth/calendar']


class GoogleCalendarManager:
    """
    Googleカレンダーの操作を管理するクラス。
    """
    
    def __init__(self, credentials_file="credentials.json", token_file ="token.json"):
        """
        認証情報を初期化し、Google Calendar APIへの接続を準備します。
        """
        creds = None
        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
                creds = flow.run_console()
        
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
            
        self.service = build("calendar", "v3", credentials=creds)

    def create_event(self, event: CalendarEvent) -> None:
        """
        新しいイベントをGoogleカレンダーに登録します。
        """
        event_body = {
            "summary": event.title,
            "description": event.description,
            "start": {
                "dateTime": event.start_time.isoformat(),
                "timeZone": "Asia/Tokyo",
            },
            "end": {
                "dateTime": event.end_time.isoformat(),
                "timeZone": "Asia/Tokyo",
            },
        }
        
        try:
            created_event = self.service.events().insert(calendarId='primary', body=event_body).execute()
            print(f"Event created: {created_event.get('htmlLink')}")
        except HttpError as error:
            print(f"An error occurred: {error}")

    def search_events(
        self, 
        start_time: datetime.datetime, 
        end_time: datetime.datetime, 
        query: str | None = None
    ) -> List[Dict[str, Any]]:
        """
        指定された期間とクエリでイベントを検索します。

        Args:
            start_time: 検索範囲の開始日時。
            end_time: 検索範囲の終了日時。
            query: 検索キーワード（任意）。

        Returns:
            見つかったイベントのリスト。
        """
        try:
            events_result = self.service.events().list(
                calendarId='primary', 
                timeMin=start_time.isoformat() + 'Z', # 'Z'はUTCを示す
                timeMax=end_time.isoformat() + 'Z',
                q=query,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            return events_result.get('items', [])
        except HttpError as error:
            print(f"An error occurred: {error}")
            return []

    def delete_event(self, event_id: str) -> bool:
        """
        指定されたIDのイベントを削除します。

        Args:
            event_id: 削除するイベントのID。

        Returns:
            削除が成功した場合はTrue、失敗した場合はFalse。
        """
        try:
            self.service.events().delete(calendarId='primary', eventId=event_id).execute()
            print(f"Event with ID: {event_id} deleted successfully.")
            return True
        except HttpError as error:
            print(f"An error occurred while deleting event {event_id}: {error}")
            return False
