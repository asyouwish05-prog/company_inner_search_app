"""
このファイルは、Webアプリのメイン処理が記述されたファイルです。
"""

############################################################
# 1. ライブラリの読み込み
############################################################
# 「.env」ファイルから環境変数を読み込むための関数
from dotenv import load_dotenv
# ログ出力を行うためのモジュール
import logging
# streamlitアプリの表示を担当するモジュール
import streamlit as st
# （自作）画面表示以外の様々な関数が定義されているモジュール
import utils
# （自作）アプリ起動時に実行される初期化処理が記述された関数
from initialize import initialize
# （自作）画面表示系の関数が定義されているモジュール
import components as cn
# （自作）変数（定数）がまとめて定義・管理されているモジュール
import constants as ct

#追加
import os

# --- ここから追加 ---
# LangChainのデバッグログを有効にする
# initialize()関数のエラーより前に実行されるように、この位置に置く
os.environ["LANGCHAIN_TRACING_V2"] = "false"  # トレースを無効化
os.environ["LANGCHAIN_VERBOSE"] = "true"     # ログを詳細化
logging.basicConfig(level=logging.DEBUG)     # Pythonの標準ログレベルをDEBUGに設定
# --- PDFminerのログ抑制 (新たに追加) ---
# pdfminer.six のログレベルを WARNING に設定し、大量のDEBUG出力を抑制
logging.getLogger("pdfminer").setLevel(logging.WARNING)
# --- ここから追記 ---
# watchdog のログレベルを WARNING に設定し、大量のDEBUG出力を抑制
logging.getLogger("watchdog").setLevel(logging.WARNING)
# --- ここまで追記 ---

############################################################
# 2. 設定関連
############################################################
# ブラウザタブの表示文言を設定
st.set_page_config(
    page_title=ct.APP_NAME
)

# ログ出力を行うためのロガーの設定
logger = logging.getLogger(ct.LOGGER_NAME)


############################################################
# 3. 初期化処理
############################################################
try:
    # 初期化処理（「initialize.py」の「initialize」関数を実行）
    initialize()
except Exception as e:
    # エラーログの出力
    logger.error(f"{ct.INITIALIZE_ERROR_MESSAGE}\n{e}")
    # エラーメッセージの画面表示
    st.error(utils.build_error_message(ct.INITIALIZE_ERROR_MESSAGE), icon=ct.ERROR_ICON)
    # 後続の処理を中断
    st.stop()

# アプリ起動時のログファイルへの出力
if not "initialized" in st.session_state:
    st.session_state.initialized = True
    logger.info(ct.APP_BOOT_MESSAGE)

# --- 追記：st.session_state.mode の初期化 ---
# 4. 初期表示の前に mode を定義しておくことで、チャット履歴表示などでのエラーを防ぐ
if "mode" not in st.session_state:
    st.session_state.mode = ct.ANSWER_MODE_1 # デフォルトのモードを設定

############################################################
# 4. 初期表示
############################################################
# タイトル表示
#cn.display_app_title()

# モード表示
#cn.display_select_mode()

# AIメッセージの初期表示
#cn.display_initial_ai_message()

# タイトル表示
cn.display_app_title()

# --------------------------------------------------------------------------------
# 【サイドバーの構成】
# --------------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 利用目的")

    # 利用目的の選択肢をラジオボタンで表示
    selected_mode = st.radio(
        "モードを選択してください",
        [ct.ANSWER_MODE_1, ct.ANSWER_MODE_2],
        key="sidebar_selected_mode",
        label_visibility="collapsed"
    )
    # セッションステートに保存
    st.session_state.mode = selected_mode

    # 横線を追加
    st.markdown("---")

   # モードごとの説明を表示
    if st.session_state.mode == ct.ANSWER_MODE_1:
        # 社内文書検索モードの説明
        col_icon, col_text = st.columns([0.05, 0.95]) 
        
        with col_icon:
            st.markdown(ct.DOC_SOURCE_ICON) 
            
        with col_text:
            # 説明文（st.infoはそのまま）
            st.info("入力内容と関連性が高い社内文書のありかを検索できます。") 
            
            # --- 変更箇所：color: #000; を追加 ---
            st.markdown(
                """
                <div style='background-color: #eee; padding: 10px; border-radius: 5px; white-space: pre-wrap; word-break: break-word; **color: #000;**'>
                【入力例】 社員の育成方針に関するMTGの議事録
                </div>
                """,
                unsafe_allow_html=True
            )
            # ----------------------------------------------------------------------
        
    elif st.session_state.mode == ct.ANSWER_MODE_2:
        # 社内問い合わせモードの説明
        col_icon_2, col_text_2 = st.columns([0.05, 0.95]) 

        with col_icon_2:
            st.markdown(ct.ASSISTANT_ICON)

        with col_text_2:
            # 説明文（st.infoはそのまま）
            st.info("質問・要望に対して、社内文書の情報をもとに回答を得られます。")
            
            # --- 変更箇所：color: #000; を追加 ---
            st.markdown(
                """
                <div style='background-color: #eee; padding: 10px; border-radius: 5px; white-space: pre-wrap; word-break: break-word; **color: #000;**'>
                【入力例】 人事部に所属している従業員情報を一覧化して
                </div>
                """,
                unsafe_allow_html=True
            )
            # ----------------------------------------------------------------------
# --------------------------------------------------------------------------------
# 【メイン画面のメッセージ】 (cn.display_initial_ai_message() の内容を置き換え)
# --------------------------------------------------------------------------------

# ウェルカムメッセージ (薄緑の背景: st.success を使用)
#st.success(f"{ct.DOC_SOURCE_ICON}{ct.WELCOME_MESSAGE}")
# 変更後（アイコンとメッセージを分離し、メッセージのみを st.success で囲む）:
col1, col2 = st.columns([0.05, 0.95]) # 5%と95%の幅で2列に分割

# 左の列（アイコン）
with col1:
    # ロボットアイコン (新しく定義した ct.ASSISTANT_ICON を使用)
    st.markdown(ct.ASSISTANT_ICON)

# 右の列（メッセージボックス）
with col2:
    # メッセージのみを st.success で囲み、薄緑の背景を維持
    st.success(ct.WELCOME_MESSAGE)

# 注意書き (薄黄色の背景: st.warning を使用)
# 注意書きも同様にアイコンとメッセージを分離し、配置をウェルカムメッセージと揃える
col3, col4 = st.columns([0.05, 0.95]) # アイコンとメッセージ本文の列分割

# 左の列（アイコン）
with col3:
    # 警告アイコン (ct.WARNING_ICON を使用)
    st.markdown(ct.WARNING_ICON) 

# 右の列（メッセージボックス）
with col4:
    # メッセージのみを st.warning で囲み、薄黄色の背景を維持
    st.warning(ct.INPUT_HINT_MESSAGE)


############################################################
# 5. 会話ログの表示
############################################################
try:
    # 会話ログの表示
    cn.display_conversation_log()
except Exception as e:
    # エラーログの出力
    logger.error(f"{ct.CONVERSATION_LOG_ERROR_MESSAGE}\n{e}")
    # エラーメッセージの画面表示
    st.error(utils.build_error_message(ct.CONVERSATION_LOG_ERROR_MESSAGE), icon=ct.ERROR_ICON)
    # 後続の処理を中断
    st.stop()


############################################################
# 6. チャット入力の受け付け
############################################################
chat_message = st.chat_input(ct.CHAT_INPUT_HELPER_TEXT)


############################################################
# 7. チャット送信時の処理
############################################################
if chat_message:
    # ==========================================
    # 7-1. ユーザーメッセージの表示
    # ==========================================
    # ユーザーメッセージのログ出力
    logger.info({"message": chat_message, "application_mode": st.session_state.mode})

    # ユーザーメッセージを表示
    with st.chat_message("user"):
        st.markdown(chat_message)

    # ==========================================
    # 7-2. LLMからの回答取得
    # ==========================================
    # 「st.spinner」でグルグル回っている間、表示の不具合が発生しないよう空のエリアを表示
    res_box = st.empty()
    # LLMによる回答生成（回答生成が完了するまでグルグル回す）
    with st.spinner(ct.SPINNER_TEXT):
        try:
            # 画面読み込み時に作成したRetrieverを使い、Chainを実行
            llm_response = utils.get_llm_response(chat_message)
        except Exception as e:
            # エラーログの出力
            logger.error(f"{ct.GET_LLM_RESPONSE_ERROR_MESSAGE}\n{e}")
            # エラーメッセージの画面表示
            st.error(utils.build_error_message(ct.GET_LLM_RESPONSE_ERROR_MESSAGE), icon=ct.ERROR_ICON)
            # 後続の処理を中断
            st.stop()
    
    # ==========================================
    # 7-3. LLMからの回答表示
    # ==========================================
    with st.chat_message("assistant"):
        try:
            # ==========================================
            # モードが「社内文書検索」の場合
            # ==========================================
            if st.session_state.mode == ct.ANSWER_MODE_1:
                # 入力内容と関連性が高い社内文書のありかを表示
                content = cn.display_search_llm_response(llm_response)

            # ==========================================
            # モードが「社内問い合わせ」の場合
            # ==========================================
            elif st.session_state.mode == ct.ANSWER_MODE_2:
                # 入力に対しての回答と、参照した文書のありかを表示
                content = cn.display_contact_llm_response(llm_response)
            
            # AIメッセージのログ出力
            logger.info({"message": content, "application_mode": st.session_state.mode})
        except Exception as e:
            # エラーログの出力
            logger.error(f"{ct.DISP_ANSWER_ERROR_MESSAGE}\n{e}")
            # エラーメッセージの画面表示
            st.error(utils.build_error_message(ct.DISP_ANSWER_ERROR_MESSAGE), icon=ct.ERROR_ICON)
            # 後続の処理を中断
            st.stop()

    # ==========================================
    # 7-4. 会話ログへの追加
    # ==========================================
    # 表示用の会話ログにユーザーメッセージを追加
    st.session_state.messages.append({"role": "user", "content": chat_message})
    # 表示用の会話ログにAIメッセージを追加
    st.session_state.messages.append({"role": "assistant", "content": content})