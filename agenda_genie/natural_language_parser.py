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

from .schemas import CalendarEvent, ParsedResult, ActionType


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


    def parse_event_text(self, text: str) -> ParsedResult | None:
        """
        与えられたテキストからユーザーの意図とイベント情報を抽出し、ParsedResultオブジェクトを生成します。

        Args:
            text: ユーザーによって入力された自然言語のテキスト。

        Returns:
            抽出された情報を持つParsedResultオブジェクト。抽出に失敗した場合はNone。
        """
        now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

        # プロンプトテンプレートのプレースホルダーを実際の値で置換
        prompt = self.prompt_template.format(now=now_str, user_text=text)

        try:
            response = self.model.generate_content(prompt)
            # Geminiからの応答テキストをクリーンアップ
            json_text = response.text.strip().lstrip("```json").rstrip("```").strip()
            
            # JSON文字列をPythonの辞書に変換
            parsed_data = json.loads(json_text)
            
            action_str = parsed_data.get("action")
            if not action_str:
                raise ValueError("JSON応答に'action'キーが含まれていません。")

            action = ActionType(action_str)

            if action == ActionType.CREATE:
                event_data = parsed_data["event"]
                event = CalendarEvent(
                    title=event_data["title"],
                    start_time=datetime.datetime.fromisoformat(event_data["start_time"]),
                    end_time=datetime.datetime.fromisoformat(event_data["end_time"]),
                    description=event_data.get("description"),
                )
                return ParsedResult(action=action, event=event)
            
            elif action == ActionType.DELETE:
                search_info = parsed_data["event"]
                return ParsedResult(action=action, event=search_info)
            
            elif action in [ActionType.READ, ActionType.TALK]:
                original_text = parsed_data.get("original_text", text)
                return ParsedResult(action=action, original_text=original_text)

            else:
                # 未知のactionタイプの場合は、TALKとして扱う
                return ParsedResult(action=ActionType.TALK, original_text=text)

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"イベント情報の解析中にエラーが発生しました: {e}")
            if 'response' in locals():
                print(f"Geminiからの応答: {response.text}")
            # 解析に失敗した場合は、雑談として扱う
            return ParsedResult(action=ActionType.TALK, original_text=text)