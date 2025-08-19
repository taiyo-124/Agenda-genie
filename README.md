# Agenda Genie

「Agenda Genie」は、生成AIとGoogleカレンダーを連携させ、LINEを通じて手軽にスケジュール管理ができるアプリケーションです。

## 概要

LINEのチャットインターフェースを通じて、自然な対話形式で予定の追加、確認、変更が可能です。バックエンドでは生成AIがユーザーの意図を解釈し、Googleカレンダーに自動的にスケジュールを登録・操作します。

## 主な機能（構想）

- **自然言語でのスケジュール登録:** 「明日の14時にAさんと会議」のようなメッセージでGoogleカレンダーに予定を追加。
- **予定の確認と一覧表示:** 「今週の予定は？」と聞くだけでGoogleカレンダーから予定を取得し、LINEに表示。
- **柔軟な予定変更・削除:** チャットで簡単にスケジュールの変更やキャンセルが可能。

## 技術スタック

- **言語:** Python
- **AI:** Google Gemini API
- **プラットフォーム:** Google Calendar API, LINE Messaging API (予定)
- **主要ライブラリ:**
  - `google-api-python-client`, `google-auth-oauthlib` (Google Calendar連携)
  - `google-generativeai` (Gemini API連携)
  - `python-dotenv` (環境変数管理)
- **コード品質:** Ruff, Mypy

## 開発ロードマップ

### ✔️ ステップ1: データ構造の定義 (実装済み)

アプリケーションの核となる`CalendarEvent`クラスを`agenda_genie/schemas.py`に定義しました。これにより、AIが解析すべきデータのゴールが明確になりました。

### ✔️ ステップ2: Googleカレンダー連携モジュールの作成 (実装済み)

`CalendarEvent`オブジェクトを受け取り、Google Calendar APIを呼び出して実際にカレンダーへ予定を登録する`GoogleCalendarManager`クラスを`agenda_genie/google_calendar.py`に実装しました。

### ✔️ ステップ3: 生成AIによる自然言語解析 (実装済み)

ユーザーの自然な文章をGemini APIで解析し、`CalendarEvent`オブジェクトに変換する`GeminiParser`クラスを`agenda_genie/natural_language_parser.py`に実装しました。プロンプトは外部ファイル (`prompts/parse_event.md`) で管理しています。

### ステップ4: LINE Botインターフェースの構築

最後に、これらすべての機能を統合します。LINEからのメッセージを受信し、AIモジュールで解析し、Googleカレンダー連携モジュールで予定を登録し、最終的にLINEユーザーへ応答メッセージを返す、一連の流れを完成させます。

具体的な開発フローは以下の通りです。

1.  **Webサーバーの準備とライブラリの追加**:
    -   LINEプラットフォームからのリクエストを受け取るため、Webフレームワーク **Flask** を導入します。
    -   LINE APIを操作するための **`line-bot-sdk`** をプロジェクトに追加します。

2.  **LINE Botサーバーの基本構造を作成**:
    -   Webサーバーのエントリーポイントとなる `app.py` を作成します。
    -   LINEチャネルのシークレットとアクセストークンを `.env` ファイルから安全に読み込むように設定します。

3.  **Webhookエンドポイントの実装**:
    -   LINEからのメッセージ通知（Webhook）を受け取るためのAPIエンドポイントを実装します。
    -   受信したメッセージがテキストであれば、次の処理に進むロジックを記述します。

4.  **既存機能との統合**:
    -   受信したテキストを `GeminiParser` に渡し、`CalendarEvent` オブジェクトに変換します。
    -   変換に成功した場合、`GoogleCalendarManager` を使ってカレンダーに予定を登録します。
    -   処理結果（成功・失敗）に応じて、ユーザーに返信メッセージを送信します。

5.  **テスト**:
    -   ローカル環境でサーバーを起動し、`ngrok` 等を用いて一時的な公開URLを取得します。
    -   LINE DevelopersコンソールにWebhook URLを設定し、実際にLINEアプリからメッセージを送信して動作を確認します。

## セットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/taiyo-124/Agenda-genie.git
cd Agenda-genie
```

### 2. 仮想環境の作成と有効化

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. 依存ライブラリのインストール

```bash
pip install -r requirements.txt
```

### 4. Google Calendar API の設定

1. Google Cloud Platformでプロジェクトを作成し、Google Calendar APIを有効にします。
2. 「APIとサービス」>「認証情報」に移動し、「認証情報を作成」から「OAuth 2.0 クライアント ID」を選択します。
3. アプリケーションの種類で「デスクトップアプリ」を選択し、名前を付けて作成します。
4. 作成された認証情報のJSONファイルをダウンロードし、プロジェクトのルートディレクトリに`credentials.json`という名前で保存します。

### 5. Gemini APIキーの設定

1. [Google AI Studio](https://aistudio.google.com/app/apikey)にアクセスし、APIキーを取得します。
2. プロジェクトのルートディレクトリに`.env`という名前のファイルを作成します。
3. `.env`ファイルに以下の内容を記述し、ご自身のAPIキーに置き換えてください。

```
GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

## 使い方 (CLIでのテスト)

セットアップ完了後、コマンドラインからアプリケーションの動作をテストできます。

### 初回認証

最初にGoogleカレンダー連携機能を使う際、Googleアカウントでの認証が必要です。以下のコマンドを実行すると、コンソールに認証用URLが表示されます。

```bash
python -m agenda_genie.main
```

URLにアクセスしてアカウントを承認すると、コンソールにコードを貼り付けるよう求められます。認証が成功すると、`token.json`というファイルが生成され、次回以降は自動で認証されます。

### 自然言語解析機能のテスト

`GeminiParser`が様々な文章を正しく解析できるかテストするには、`--test-parser`フラグを使用します。

```bash
python -m agenda_genie.main --test-parser
```

### イベント登録のテスト

コマンドライン引数に予定を記述することで、解析からカレンダー登録までの一連の流れをテストできます。

```bash
python -m agenda_genie.main "来週の金曜19時から友人との食事"
```
