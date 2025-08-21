import os
import datetime
from dotenv import load_dotenv
from flask import Flask, request, abort

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
)

# このアプリケーションからのモジュールをインポート
from agenda_genie.google_calendar import GoogleCalendarManager
from agenda_genie.natural_language_parser import GeminiParser
from agenda_genie.schemas import ActionType

# .envファイルから環境変数を読み込む
load_dotenv()

# Flaskアプリケーションのインスタンスを作成
app = Flask(__name__)

# 環境変数からLINE Botの認証情報を取得
channel_secret = os.getenv('LINE_CHANNEL_SECRET')
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')

if not channel_secret or not channel_access_token:
    print("エラー： LINEの認証情報が.envファイルに設定されていません。")
    exit()

# LINE Messaging APIへの接続を設定
handler = WebhookHandler(channel_secret)
configuration = Configuration(access_token=channel_access_token)

# --- アプリケーションの中核部分 ---
# AIパーサーを初期化(サーバー起動時に一度だけ実行)
try:
    parser = GeminiParser()
    print("Geminiパーサーを初期化しました。")
except (ValueError, FileNotFoundError) as e:
    print(f"エラー: GeminiParserの初期化に失敗しました。{e}")
    parser = None
# --------------------------------


@app.route("/callback", methods=['POST'])
def callback():
    """
    LINEプラットフォームからのwebhookリクエストを処理するエンドポイント
    """
    # リクエストヘッダーから署名を検証
    signature = request.headers['X-Line-Signature']
    
    # リクエストボディを取得
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    
    # 署名を検証し、リクエストを処理
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel secret.")
        abort(400)
    
    return 'OK'

def handle_create(calendar_event):
    "イベント作成処理"
    try:
        manager = GoogleCalendarManager()
        manager.create_event(calendar_event)
        start_time = calendar_event.start_time.strftime("%Y/%m/%d %H:%M")
        return f"カレンダーに予定を登録しました。\n\nタイトル: {calendar_event.title}\n開始: {start_time}"
    except Exception as e:
        app.logger.error(f"カレンダーへの登録中にエラー: {e}")
        return "すみません。カレンダーへの登録中にエラーが発生しました。"


def handle_delete(search_info):
    "イベント削除処理"
    try:
        manager = GoogleCalendarManager()
        app.logger.info(f"handle_delete done using {search_info}")
        time_min = datetime.datetime.fromisoformat(search_info["start_time"])
        time_max = datetime.datetime.fromisoformat(search_info["end_time"])
        events = manager.search_events(start_time=time_min, end_time=time_max, query=search_info["key_word"])
        
        if not events:
            return f"「{search_info.key_word}」に一致する予定が見当たりませんでした。"
        elif len(events) > 1:
            # 複数見つかった場合は、ユーザーに選択を促す（今回は未実装）
            return "複数の予定が見つかりました。もう少し詳しく教えていただけますか？"
        else:
            event_to_delete = events[0]
            event_id = event_to_delete["id"]
            event_title = event_to_delete.get("summary", "無題の予定")
            if manager.delete_event(event_id=event_id):
                return f"「{event_title}」の予定を削除しました。"
            else:
                return "予定の削除に失敗しました。"            

    except Exception as e:
        app.logger.error(f"イベント削除中にエラー: {e}")
        return "予定の削除中にエラーが発生しました。"


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_text = event.message.text
    reply_text = ""

    if not parser:
        reply_text = "すみません、Genieの呼び出しに失敗しました。管理者に連絡してください。"
    else:
        parsed_result = parser.parse_event_text(user_text)

        if not parsed_result:
            reply_text = "すみません、メッセージを理解できませんでした。"
        else:
            action = parsed_result.action
            if action == ActionType.CREATE:
                reply_text = handle_create(parsed_result.event)
            elif action == ActionType.DELETE:
                reply_text = handle_delete(parsed_result.event)
            elif action == ActionType.READ:
                # TODO: 予定の読み取り機能を実装
                reply_text = "すみません、予定の確認機能はまだ準備中です。"
            elif action == ActionType.TALK:
                reply_text = parsed_result.original_text # 簡単なオウム返し
            else:
                reply_text = "すみません、予期せぬエラーが発生しました。"

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token, messages=[TextMessage(text=reply_text)]
            )
        )

if __name__ == "__main__":
    # ポート番号は環境変数'PORT'から取得、なければ8000をデフォルトとする
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)
