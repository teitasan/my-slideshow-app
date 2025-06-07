# backend/app.py
import os
import requests
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# --- アプリケーションの初期化と設定 ---
app = Flask(__name__)

# APIキーを環境変数から取得
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LEONARDO_API_KEY = os.getenv("LEONARDO_API_KEY")

# Gemini APIキーは必須（会話生成とAA生成で使用）
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEYが.envファイルに設定されていません。")

# Leonardo.Ai APIキーは画像生成モードでのみ必要（警告のみ）
if not LEONARDO_API_KEY:
    print("警告: LEONARDO_API_KEYが設定されていません。画像生成モードは使用できませんが、モックモード（AA生成）は利用可能です。")

# Gemini APIのクライアントを設定
try:
    genai.configure(api_key=GEMINI_API_KEY)
    llm = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    raise RuntimeError(f"Gemini APIの設定に失敗しました: {e}")

# Leonardo.Ai APIのエンドポイントURL
LEONARDO_API_URL = "https://cloud.leonardo.ai/api/rest/v1/generations"


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


def create_image_prompt_from_dialogue(dialogue: str) -> str:
    """会話のセリフから、画像生成に適した情景プロンプト（英語）を生成する"""
    prompt_template = load_prompt('image_prompt_generation.md')
    if not prompt_template:
        # フォールバック用のデフォルトプロンプト
        prompt_template = """以下の日本語のセリフが話されている情景を、画像生成AIが理解できるような、詳細でクリエイティブな英語のプロンプトに変換してください。
人物の感情、背景、雰囲気を豊かに表現してください。スタイルは「vibrant anime style」でお願いします。

日本語セリフ: "{dialogue}"

英語プロンプト:"""
    
    prompt = prompt_template.format(dialogue=dialogue)
    try:
        response = llm.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"画像プロンプト生成エラー: {e}")
        raise

def generate_image_from_prompt(image_prompt: str) -> str:
    """Leonardo.Ai APIを使い、プロンプトから画像を生成し、そのURLを返す"""
    if not LEONARDO_API_KEY:
        raise ValueError("画像生成モードを使用するには、LEONARDO_API_KEYを.envファイルに設定してください。モックモードをご利用いただくか、APIキーを設定してください。")
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {LEONARDO_API_KEY}"
    }
    payload = {
        "prompt": image_prompt,
        "modelId": "6bef9f1b-29cb-40c7-b9df-32b51c1f67d3", # Leonardo Anime v2
        "width": 512,
        "height": 512,
        "num_images": 1,
        "guidance_scale": 7,
    }
    try:
        response = requests.post(LEONARDO_API_URL, json=payload, headers=headers, timeout=60)
        response.raise_for_status() # HTTPエラーがあれば例外を発生
        data = response.json()
        # 生成された画像のURLを返す（APIのレスポンス構造に依存）
        return data['generations'][0]['generated_images'][0]['url']
    except requests.exceptions.RequestException as e:
        print(f"Leonardo APIリクエストエラー: {e}")
        raise
    except (KeyError, IndexError) as e:
        print(f"Leonardo APIレスポンス形式エラー: {e}, レスポンス内容: {response.text}")
        raise

def generate_aa_from_dialogue(dialogue: str, aa_style: str = "default") -> str:
    """会話のセリフから、モック用のAAを生成する"""
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

    # クエリパラメータでモックモードを判定
    is_mock_mode = request.args.get('mock') == 'true'
    aa_style = request.args.get('aa_style', 'default')  # AAスタイルを取得

    try:
        # 1. テキストから会話を生成
        dialogues = generate_conversation_from_text(user_text)
        if not dialogues:
            return jsonify({"error": "会話の生成に失敗しました。"}), 500

        if is_mock_mode:
            # --- モックモードの処理 ---
            print(f"モード: AA生成（モック）- スタイル: {aa_style}")
            data_payload = [generate_aa_from_dialogue(d, aa_style) for d in dialogues]
            response_type = "aa"
        else:
            # --- 通常モードの処理 ---
            print("モード: 画像生成（本番）")
            image_urls = []
            for dialogue in dialogues:
                image_prompt = create_image_prompt_from_dialogue(dialogue)
                image_url = generate_image_from_prompt(image_prompt)
                image_urls.append(image_url)
            data_payload = image_urls
            response_type = "image"

        return jsonify({
            "type": response_type,
            "dialogues": dialogues,
            "data": data_payload
        })

    except Exception as e:
        # 予期せぬエラーをキャッチ
        print(f"サーバー内部エラー: {e}")
        return jsonify({"error": "サーバー内部でエラーが発生しました。詳細はサーバーログを確認してください。"}), 500 