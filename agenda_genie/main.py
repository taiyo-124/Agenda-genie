import datetime

from .google_calendar import GoogleCalendarManager
from .schemas import CalendarEvent

def main():
    """
    GoogleCalendarManagerの動作をテストするためのメイン関数
    """
    print("GoogleCalendarManagerの動作テストを開始します。")
    
    # 1.GoogleCalendarManagerのインスタンスを作成
    #   初回実行時には、ブラウザが起動してGoogleアカウントでの認証が求められる
    #   承認するとプロジェクトルートに'token.json'が自動で作成される
    try:
        manager = GoogleCalendarManager()
        print("認証に成功し、Google Calendar APIへの接続を確立しました")
    except Exception as e:
        print(f"認証またはAPIへの接続中にエラーが発生しました: {e}")
        return
    
    # 2.テスト用のCalenarEventオブジェクトを作成
    #   現在の時刻から1時間後に開始し、1時間続くイベントを作成します
    now = datetime.datetime.now(datetime.timezone.utc)
    start_time = now + datetime.timedelta(hours=1)
    end_time = start_time + datetime.timedelta(hours=1)
    
    test_event = CalendarEvent(
        title="Agenda Genie: テストイベント",
        start_time=start_time,
        end_time=end_time,
        description="テスト用のイベントです"
    )
    print(f"作成するイベント: '{test_event.title}'")
    print(f"開始時刻: {test_event.start_time.astimezone().strftime('%Y-%m-%d %H:%M')}")
    print(f"終了時刻: {test_event.end_time.astimezone().strftime('%Y-%m-%d %H:%M')}")
    
    
    # 3.イベント作成メソッドを呼び出す
    try:
        print("カレンダーにイベントを登録しています")
        manager.create_event(test_event)
        print("イベントが登録されました")
    except Exception as e:
        print(f"イベントの登録中にエラーが発生しました: {e}")


if __name__ == "__main__":
    main()