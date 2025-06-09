# backend/app.py
import os
import logging
import time
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# --- ログ設定 ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # コンソール出力
    ]
)
logger = logging.getLogger(__name__)

# --- アプリケーションの初期化と設定 ---
app = Flask(__name__)

logger.info("🚀 スライドショーアプリケーションを起動中...")

# APIキーを環境変数から取得
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini APIキーは必須（会話生成とAA生成で使用）
if not GEMINI_API_KEY:
    logger.error("❌ GEMINI_API_KEYが.envファイルに設定されていません")
    raise ValueError("GEMINI_API_KEYが.envファイルに設定されていません。")

logger.info("✅ 環境変数の読み込み完了")

# Gemini APIのクライアントを設定
try:
    logger.info("🔧 Gemini APIクライアントを設定中...")
    genai.configure(api_key=GEMINI_API_KEY)
    llm = genai.GenerativeModel('gemini-1.5-flash')
    logger.info("✅ Gemini APIクライアントの設定完了")
except Exception as e:
    logger.error(f"❌ Gemini APIの設定に失敗: {e}")
    raise RuntimeError(f"Gemini APIの設定に失敗しました: {e}")


# --- ヘルパー関数 ---

def load_prompt(prompt_file: str) -> str:
    """プロンプトファイルを読み込む"""
    logger.info(f"📂 プロンプトファイルを読み込み中: {prompt_file}")
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
            result = '\n'.join(prompt_lines).strip()
            logger.info(f"✅ プロンプトファイル読み込み完了: {prompt_file} ({len(result)}文字)")
            return result
    except FileNotFoundError:
        logger.warning(f"⚠️ プロンプトファイル '{prompt_file}' が見つかりません。デフォルトプロンプトを使用します")
        return ""
    except Exception as e:
        logger.error(f"❌ プロンプトファイル読み込みエラー: {e}")
        return ""

def generate_conversation_from_text(user_text: str) -> list[str]:
    """Gemini APIを使い、入力テキストから会話形式のシナリオを生成する"""
    logger.info(f"💬 会話生成を開始 - 入力テキスト長: {len(user_text)}文字")
    start_time = time.time()
    
    prompt_template = load_prompt('conversation_generation.md')
    if not prompt_template:
        logger.info("📝 デフォルトプロンプトを使用")
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
    logger.info(f"🤖 Gemini APIに会話生成リクエストを送信中...")
    
    try:
        response = llm.generate_content(prompt)
        dialogues = [line.strip() for line in response.text.split('\n') if line.strip()]
        elapsed_time = time.time() - start_time
        
        logger.info(f"✅ 会話生成完了 - 生成されたセリフ数: {len(dialogues)}, 処理時間: {elapsed_time:.2f}秒")
        for i, dialogue in enumerate(dialogues, 1):
            logger.info(f"  💬 セリフ{i}: {dialogue[:50]}{'...' if len(dialogue) > 50 else ''}")
        
        return dialogues
    except Exception as e:
        logger.error(f"❌ Gemini API会話生成エラー: {e}")
        raise

def generate_aa_from_dialogue(dialogue: str, aa_style: str = "default") -> str:
    """会話のセリフから、AAを生成する"""
    logger.info(f"🎭 AA生成を開始 - スタイル: {aa_style}, セリフ: {dialogue[:30]}{'...' if len(dialogue) > 30 else ''}")
    start_time = time.time()
    
    prompt_template = load_prompt(f'aa_generation_{aa_style}.md')
    if not prompt_template:
        logger.error(f"❌ プロンプトファイル 'aa_generation_{aa_style}.md' が見つかりません")
        raise FileNotFoundError(f"プロンプトファイル 'aa_generation_{aa_style}.md' が見つかりません。")
    
    prompt = prompt_template.format(dialogue=dialogue)
    logger.info(f"🤖 Gemini APIにAA生成リクエストを送信中...")
    
    try:
        response = llm.generate_content(prompt)
        elapsed_time = time.time() - start_time
        aa_lines = len(response.text.split('\n'))
        
        logger.info(f"✅ AA生成完了 - 行数: {aa_lines}, 処理時間: {elapsed_time:.2f}秒")
        return response.text
    except Exception as e:
        logger.error(f"❌ Gemini API AA生成エラー: {e}")
        raise

# --- Flaskルート定義 ---

@app.route('/')
def index():
    """アプリケーションのメインページを表示する"""
    logger.info("🏠 メインページにアクセスされました")
    return render_template('index.html')


@app.route('/api/generate', methods=['POST'])
def handle_generate_request():
    """スライドショー生成リクエストを処理するAPIエンドポイント"""
    request_start_time = time.time()
    logger.info("🚀 === スライドショー生成リクエスト開始 ===")
    
    # リクエストの検証
    user_text = request.json.get('text')
    if not user_text or len(user_text.strip()) == 0:
        logger.warning("⚠️ 空のテキストが送信されました")
        return jsonify({"error": "テキストが入力されていません。"}), 400

    # AAスタイルを取得
    aa_style = request.args.get('aa_style', 'default')
    logger.info(f"📝 リクエスト詳細:")
    logger.info(f"  - 入力テキスト長: {len(user_text)}文字")
    logger.info(f"  - AAスタイル: {aa_style}")
    logger.info(f"  - 入力テキスト（最初の100文字）: {user_text[:100]}{'...' if len(user_text) > 100 else ''}")

    try:
        # 1. テキストから会話を生成
        logger.info("🔄 工程1: テキストから会話を生成中...")
        dialogues = generate_conversation_from_text(user_text)
        if not dialogues:
            logger.error("❌ 会話の生成に失敗しました（空の結果）")
            return jsonify({"error": "会話の生成に失敗しました。"}), 500

        # 2. AA生成処理
        logger.info(f"🔄 工程2: AA生成処理開始 - スタイル: {aa_style}")
        logger.info(f"🎭 {len(dialogues)}個のセリフからAAを生成中...")
        
        data_payload = []
        for i, dialogue in enumerate(dialogues, 1):
            logger.info(f"  🎯 AA生成 {i}/{len(dialogues)}: {dialogue[:30]}{'...' if len(dialogue) > 30 else ''}")
            aa_result = generate_aa_from_dialogue(dialogue, aa_style)
            data_payload.append(aa_result)
        
        response_type = "aa"
        total_elapsed_time = time.time() - request_start_time
        
        logger.info("✅ === スライドショー生成完了 ===")
        logger.info(f"📊 処理結果:")
        logger.info(f"  - 生成されたセリフ数: {len(dialogues)}")
        logger.info(f"  - 生成されたAA数: {len(data_payload)}")
        logger.info(f"  - 総処理時間: {total_elapsed_time:.2f}秒")
        logger.info(f"  - レスポンスタイプ: {response_type}")

        return jsonify({
            "type": response_type,
            "dialogues": dialogues,
            "data": data_payload
        })

    except Exception as e:
        # 予期せぬエラーをキャッチ
        error_time = time.time() - request_start_time
        logger.error(f"❌ === サーバー内部エラー ===")
        logger.error(f"エラー内容: {e}")
        logger.error(f"エラー発生時間: {error_time:.2f}秒後")
        logger.error(f"エラータイプ: {type(e).__name__}")
        return jsonify({"error": "サーバー内部でエラーが発生しました。詳細はサーバーログを確認してください。"}), 500

if __name__ == '__main__':
    logger.info("🎉 アプリケーション初期化完了")
    logger.info("🌐 サーバーを起動します...")
    app.run(debug=True, host='0.0.0.0', port=5000) 