"""
生成AIモデル(Gemini)と連携し、自然言語の解析を担当するモジュール。

ユーザーからのテキスト入力を受け取り、それを構造化された
CalendarEventデータに変換します。
"""
import datetime
import json
import os
from pathlib import Path

import google.generativeai as genai

from .schemas import CalendarEvent


class GeminiParser:
    """
    Geminiモデルを使用して自然言語を解析し、CalendarEventを生成するクラス。
    """

    def __init__(self, prompt_template_path: str | Path | None = None):
        """
        APIキーを環境変数から読み込み、Geminiモデルとプロンプトを初期化します。

        Args:
            prompt_template_path: プロンプトテンプレートファイルのパス。
                指定されない場合、デフォルトのパス "prompts/parse_event.md" を使用します。
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("APIキーが環境変数 'GEMINI_API_KEY' に設定されていません。")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

        # プロンプトテンプレートをファイルから読み込む
        if prompt_template_path is None:
            # このファイルからの相対パスでデフォルトのプロンプトパスを指定
            base_dir = Path(__file__).parent
            prompt_template_path = base_dir / "prompts" / "parse_event.md"
            
        try:
            with open(prompt_template_path, 'r', encoding='utf-8') as f:
                self.prompt_template = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"プロンプトファイルが見つかりません: {prompt_template_path}")


    def parse_event_text(self, text: str) -> CalendarEvent | None:
        """
        与えられたテキストからイベント情報を抽出し、CalendarEventオブジェクトを生成します。

        Args:
            text: ユーザーによって入力された自然言語のテキスト。

        Returns:
            抽出された情報を持つCalendarEventオブジェクト。抽出に失敗した場合はNone。
        """
        now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

        # プロンプトテンプレートのプレースホルダーを実際の値で置換
        prompt = self.prompt_template.format(now=now_str, user_text=text)

        try:
            response = self.model.generate_content(prompt)
            json_text = response.text.strip().replace("```json", "").replace("```", "").strip()
            
            if "incomplete" in json_text:
                print("日時が不明確なため、イベントを生成できませんでした。")
                return None

            event_data = json.loads(json_text)

            return CalendarEvent(
                title=event_data["title"],
                start_time=datetime.datetime.fromisoformat(event_data["start_time"]),
                end_time=datetime.datetime.fromisoformat(event_data["end_time"]),
                description=event_data.get("description"),
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"イベント情報の解析中にエラーが発生しました: {e}")
            # エラー発生時にAIからの生の応答も表示するとデバッグしやすい
            if 'response' in locals():
                print(f"Geminiからの応答: {response.text}")
            return None