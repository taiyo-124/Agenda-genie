import sys
from dotenv import load_dotenv

from .google_calendar import GoogleCalendarManager
from .natural_language_parser import GeminiParser

# .envファイルから環境変数を読み込む
load_dotenv()


def test_parser():
    """
    GeminiParserの動作をテストするための関数。
    いくつかの例文を解析し、結果を表示する。
    """
    print("--- GeminiParserのテストを開始します ---")
    
    # テスト用の例文リスト
    test_cases = [
        "明日の15時からクライアントと30分間の打ち合わせ",
        "来週の月曜、朝9時から定例会議",
        "今日の午後8時にオンラインで勉強会。内容はPythonについて。",
        "1週間後の13時半に歯医者を予約",
        "渋谷でランチ", # -> 日時が不明確なため失敗するはず
    ]

    try:
        parser = GeminiParser()
    except (ValueError, FileNotFoundError) as e:
        print(f"エラー: パーサーの初期化に失敗しました。 {e}")
        return

    for i, text in enumerate(test_cases, 1):
        print(f"\n[テストケース {i}]")
        print(f"入力テキスト: '{text}'")
        
        event = parser.parse_event_text(text)
        
        if event:
            print("-> 解析成功:")
            print(f"   タイトル: {event.title}")
            print(f"   開始時刻: {event.start_time.strftime('%Y-%m-%d %H:%M')}")
            print(f"   終了時刻: {event.end_time.strftime('%Y-%m-%d %H:%M')}")
            print(f"   説明: {event.description or 'なし'}")
        else:
            print("-> 解析失敗または情報不十分")
    
    print("\n--- テストを終了します ---")


def main():
    """
    コマンドラインから受け取った自然言語のテキストを解析し、
    Googleカレンダーにイベントを登録するメイン関数。
    --test-parser フラグが指定された場合は、パーサーのテストを実行する。
    """
    # --test-parser フラグがあるかチェック
    if "--test-parser" in sys.argv:
        test_parser()
        return

    # --- 通常のイベント登録処理 ---
    
    # コマンドライン引数からテキストを取得 (フラグは除外)
    args = [arg for arg in sys.argv[1:] if arg != "--test-parser"]
    if args:
        event_text = " ".join(args)
    else:
        event_text = "明日の15時からクライアントと30分間の打ち合わせ"
        print("コマンドライン引数が指定されなかったため、テスト用のテキストを使用します。")
        print(f"テキスト: '{event_text}'")

    # 1. 自然言語解析器を初期化
    try:
        print("Geminiパーサーを初期化しています...")
        parser = GeminiParser()
        print("初期化完了。")
    except (ValueError, FileNotFoundError) as e:
        print(f"エラー: {e}")
        print("環境変数 'GEMINI_API_KEY' やプロンプトファイルのパスを確認してください。")
        return

    # 2. テキストを解析してCalendarEventオブジェクトを取得
    print(f"'{event_text}' の解析を開始します...")
    calendar_event = parser.parse_event_text(event_text)

    # 3. 解析結果の確認とイベント登録
    if calendar_event:
        print("\n--- 解析結果 ---")
        print(f"タイトル: {calendar_event.title}")
        print(f"開始時刻: {calendar_event.start_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"終了時刻: {calendar_event.end_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"説明: {calendar_event.description or 'なし'}")
        print("-----------------\n")

        # 4. Googleカレンダーにイベントを登録
        try:
            print("Googleカレンダーへの接続を開始します...")
            manager = GoogleCalendarManager()
            print("接続完了。イベントを登録しています...")
            manager.create_event(calendar_event)
            print("イベントの登録が完了しました。")
        except Exception as e:
            print(f"Googleカレンダーへのイベント登録中にエラーが発生しました: {e}")
    else:
        print("テキストからイベント情報を抽出できませんでした。")


if __name__ == "__main__":
    main()
