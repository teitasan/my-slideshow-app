# backend/app.py
import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# --- アプリケーションの初期化と設定 ---
app = Flask(__name__)

# APIキーを環境変数から取得
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini APIキーは必須（会話生成とAA生成で使用）
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEYが.envファイルに設定されていません。")

# Gemini APIのクライアントを設定
try:
    genai.configure(api_key=GEMINI_API_KEY)
    llm = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    raise RuntimeError(f"Gemini APIの設定に失敗しました: {e}")


# --- ヘルパー関数 ---

def load_prompt(prompt_file: str) -> str:
    """プロンプトファイルを読み込む"""
    try:
        prompt_path = os.path.join(os.path.dirname(__file__), 'prompts', prompt_file)
        with open(prompt_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Markdownのタイトル行（# で始まる行）を除去してプロンプト部分のみを返す
            lines = content.split('\n')
            prompt_lines = []
            for line in lines:
                if not line.strip().startswith('#') and line.strip():
                    prompt_lines.append(line)
                elif prompt_lines:  # タイトル後の空行以降を含める
                    prompt_lines.append(line)
            return '\n'.join(prompt_lines).strip()
    except FileNotFoundError:
        print(f"警告: プロンプトファイル '{prompt_file}' が見つかりません。デフォルトプロンプトを使用します。")
        return ""
    except Exception as e:
        print(f"プロンプトファイル読み込みエラー: {e}")
        return ""

def generate_conversation_from_text(user_text: str) -> list[str]:
    """Gemini APIを使い、入力テキストから会話形式のシナリオを生成する"""
    prompt_template = load_prompt('conversation_generation.md')
    if not prompt_template:
        # フォールバック用のデフォルトプロンプト
        prompt_template = """以下の文章を、AさんとBさんの2人が会話しているような自然な対話形式のシナリオに書き換えてください。
シナリオは面白く、創造的にしてください。各セリフは必ず改行で区切ってください。
例:
A: 今日はいい天気だね！
B: 本当だね。どこかに出かけたくなるよ。

--- START OF TEXT ---
{user_text}
--- END OF TEXT ---"""
    
    prompt = prompt_template.format(user_text=user_text)
    try:
        response = llm.generate_content(prompt)
        # 空白行を除外し、セリフのみのリストを返す
        return [line.strip() for line in response.text.split('\n') if line.strip()]
    except Exception as e:
        print(f"Gemini APIエラー: {e}")
        raise

def generate_aa_from_dialogue(dialogue: str, aa_style: str = "default") -> str:
    """会話のセリフから、AAを生成する"""
    prompt_template = load_prompt(f'aa_generation_{aa_style}.md')
    if not prompt_template:
        raise FileNotFoundError(f"プロンプトファイル 'aa_generation_{aa_style}.md' が見つかりません。")
    
    prompt = prompt_template.format(dialogue=dialogue)
    response = llm.generate_content(prompt)
    return response.text

# --- Flaskルート定義 ---

@app.route('/')
def index():
    """アプリケーションのメインページを表示する"""
    return render_template('index.html')


@app.route('/api/generate', methods=['POST'])
def handle_generate_request():
    """スライドショー生成リクエストを処理するAPIエンドポイント"""
    user_text = request.json.get('text')
    if not user_text or len(user_text.strip()) == 0:
        return jsonify({"error": "テキストが入力されていません。"}), 400

    # AAスタイルを取得
    aa_style = request.args.get('aa_style', 'default')

    try:
        # 1. テキストから会話を生成
        dialogues = generate_conversation_from_text(user_text)
        if not dialogues:
            return jsonify({"error": "会話の生成に失敗しました。"}), 500

        # AA生成処理
        print(f"モード: AA生成 - スタイル: {aa_style}")
        data_payload = [generate_aa_from_dialogue(d, aa_style) for d in dialogues]
        response_type = "aa"

        return jsonify({
            "type": response_type,
            "dialogues": dialogues,
            "data": data_payload
        })

    except Exception as e:
        # 予期せぬエラーをキャッチ
        print(f"サーバー内部エラー: {e}")
        return jsonify({"error": "サーバー内部でエラーが発生しました。詳細はサーバーログを確認してください。"}), 500 