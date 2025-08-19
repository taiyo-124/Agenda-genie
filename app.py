import os 
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

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    """
    テキストメッセージを受信したときの処理
    """
    user_text = event.message.text
    reply_text = ""
    
    # パーサーが正常に初期化されているかチェック
    if not parser:
        reply_text = "すみません、Genieの呼び出しに失敗しました。管理者に連絡してください。"
    else:
        try:
            # 1.ユーザーのテキストを解析
            app.logger.info(f"ユーザーからのテキスト: {user_text}")
            calendar_event = parser.parse_event_text(user_text)
            
            if calendar_event:
                # 2.解析成功 -> Googleカレンダーに登録
                app.logger.info(f"解析成功: '{user_text}'")
                try:
                    manager = GoogleCalendarManager()
                    manager.create_event(calendar_event)
                    
                    # 成功メッセージを作成
                    start_time = calendar_event.start_time.strftime('%Y/%m/%d %H:%M')
                    reply_text = (
                        "カレンダーに予定を登録しました。\n\n"
                        f"タイトル: {calendar_event.title}\n"
                        f"開始: {start_time}\n"
                    )
                    app.logger.info("カレンダーへの登録成功")
                except Exception as e:
                    app.logger.error(f"カレンダーへの登録中にエラー: {e}")
                    reply_text = "すみません。カレンダーへの登録中にエラーが発生しました。"
            else:
                # 3.解析失敗
                app.logger.info("解析失敗または情報不十分")
                reply_text = "すみません。予定をうまく読み取れませんでした。日時がわかるようにもう少し具体的に教えていただけますか？"
        
        except Exception as e:
            app.logger.error(f"メッセージ処理中に予期せぬエラー: {e}")
            reply_text = "すみません、予期せぬエラーが発生しました。管理者に連絡してください。"
    
    # 4.ユーザーに返信
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)]
            )   
        )

if __name__ == "__main__":
    # ポート番号は環境変数'PORT'から取得、なければ8000をデフォルトとする
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)