import streamlit as st
import pandas as pd
import random
import json
from typing import Dict, Optional
import gspread
from oauth2client.service_account import ServiceAccountCredentials


class Word:
    """單字資料類別"""
    
    def __init__(self, word: str, explanation: str, related_words: str, 
                 pos: str, usage: str, sentence: str):
        self.word = word
        self.explanation = explanation
        self.related_words = related_words
        self.pos = pos
        self.usage = usage
        self.sentence = sentence
    
    def to_dict(self) -> Dict:
        """轉換為字典格式"""
        return {
            'word': self.word,
            'explanation': self.explanation,
            'related_words': self.related_words,
            'pos': self.pos,
            'usage': self.usage,
            'sentence': self.sentence
        }


class GoogleSheetConnector:
    """Google Sheet 連接器"""
    
    def __init__(self):
        self.credentials = None
        self.client = None
        self.sheet = None
    
    def setup_credentials_from_secrets(self):
        """設置 Google Sheet 憑證"""
        try:

            scope = ['https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/drive']
            self.credentials = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(st.secrets['gsheet-conn']['credits']), scope)
            self.client = gspread.authorize(self.credentials)
            return True
        except Exception as e:
            st.error(f"憑證設置失敗: {e}")
            return False
    
    def connect_sheet(self, sheet_url: str, worksheet_name: str = "工作表1"):
        """連接到指定的 Google Sheet"""
        try:
            self.sheet = self.client.open_by_url(sheet_url).worksheet(worksheet_name)
            return True
        except Exception as e:
            st.error(f"連接 Google Sheet 失敗: {e}")
            return False
    
    def fetch_vocabulary_data(self) -> pd.DataFrame:
        """從 Google Sheet 獲取單字資料"""
        try:
            data = self.sheet.get_all_records()
            return pd.DataFrame(data)
        except Exception as e:
            st.error(f"獲取資料失敗: {e}")
            return pd.DataFrame()


class VocabularyCard:
    """單字卡片類別"""
    
    def __init__(self, word: Word):
        self.word = word
        self.is_flipped = False
    
    def flip_card(self):
        """翻轉卡片"""
        self.is_flipped = not self.is_flipped
    
    def reset_card(self):
        """重置卡片到正面（英文）"""
        self.is_flipped = False
    
    def render_front(self):
        """渲染卡片正面（英文）"""
        st.markdown(f"""
        <div style="
            border: 2px solid #D4B5A0;
            border-radius: 20px;
            padding: 40px;
            text-align: center;
            background: linear-gradient(135deg, #F5F1EB 0%, #E8DDD4 100%);
            box-shadow: 0 8px 25px rgba(186, 159, 143, 0.2);
            margin: 20px 0;
            position: relative;
            overflow: hidden;
        ">
            <div style="
                position: absolute;
                top: -50px;
                right: -50px;
                width: 100px;
                height: 100px;
                background: radial-gradient(circle, rgba(212, 181, 160, 0.1) 0%, transparent 70%);
            "></div>
            <h1 style="
                color: #8B7B6B; 
                font-size: 2.5em; 
                margin-bottom: 20px;
                font-weight: 300;
                letter-spacing: 2px;
                text-shadow: 1px 1px 2px rgba(139, 123, 107, 0.1);
            ">{self.word.word}</h1>
            <div style="
                background: rgba(186, 159, 143, 0.15);
                padding: 15px 25px;
                border-radius: 25px;
                margin: 20px auto;
                display: inline-block;
            ">
                <h3 style="color: #A08B7A; margin: 0; font-weight: 400;">({self.word.pos})</h3>
            </div>
            <p style="
                color: #9B8F84; 
                font-style: italic; 
                font-size: 1.2em;
                margin-top: 25px;
                line-height: 1.6;
            ">{self.word.usage}</p>
            <p style="color: #6B5D56; margin: 12px 0; font-size: 1.1em; line-height: 1.5;">
                    <span style="color: #7A6E65; font-style: italic;">{self.word.sentence}</span>
                </p>
        </div>
        """, unsafe_allow_html=True)

    def render_back(self):
        """渲染卡片背面（中文釋義）"""
        st.markdown(f"""
        <div style="
            border: 2px solid #C4A69C;
            border-radius: 20px;
            padding: 40px;
            text-align: center;
            background: linear-gradient(135deg, #F0E6E0 0%, #E5D5CE 100%);
            box-shadow: 0 8px 25px rgba(196, 166, 156, 0.25);
            margin: 20px 0;
            position: relative;
            overflow: hidden;
        ">
            <div style="
                position: absolute;
                top: -30px;
                left: -30px;
                width: 80px;
                height: 80px;
                background: radial-gradient(circle, rgba(196, 166, 156, 0.08) 0%, transparent 70%);
            "></div>
            <h1 style="
                color: #8B7B6B; 
                font-size: 3.2em; 
                margin-bottom: 20px;
                font-weight: 300;
                letter-spacing: 1px;
            ">{self.word.word}</h1>
            <h2 style="
                color: #A0827A; 
                margin-bottom: 30px;
                font-weight: 400;
                font-size: 1.8em;
            ">{self.word.explanation}</h2>
            <div style="
                text-align: left; 
                background: rgba(255, 250, 247, 0.95); 
                padding: 25px; 
                border-radius: 15px; 
                margin: 20px 0;
                border: 1px solid rgba(196, 166, 156, 0.2);
            ">
                <p style="color: #6B5D56; margin: 12px 0; font-size: 1.1em; line-height: 1.5;">
                    <strong style="color: #8B7B6B; font-weight: 500;">詞性:</strong> 
                    <span style="color: #A08B7A;">{self.word.pos}</span>
                </p>
                <p style="color: #6B5D56; margin: 12px 0; font-size: 1.1em; line-height: 1.5;">
                    <strong style="color: #8B7B6B; font-weight: 500;">用法:</strong> 
                    <span style="color: #7A6E65;">{self.word.usage}</span>
                </p>
                <p style="color: #6B5D56; margin: 12px 0; font-size: 1.1em; line-height: 1.5;">
                    <strong style="color: #8B7B6B; font-weight: 500;">相關詞彙:</strong> 
                    <span style="color: #A08B7A;">{self.word.related_words}</span>
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)


class VocabularyManager:
    """單字管理器"""
    
    def __init__(self):
        self.sheet_connector = GoogleSheetConnector()
        # 初始化 session state 中的單字列表
        if 'vocabulary_list' not in st.session_state:
            st.session_state.vocabulary_list = []
    
    @property
    def vocabulary_list(self):
        """獲取單字列表"""
        return st.session_state.vocabulary_list
    
    @vocabulary_list.setter
    def vocabulary_list(self, value):
        """設置單字列表"""
        st.session_state.vocabulary_list = value
    
    def load_vocabulary_from_sheet(self, sheet_url: str):
        """從 Google Sheet 載入單字資料"""
        if self.sheet_connector.setup_credentials_from_secrets():
            if self.sheet_connector.connect_sheet(sheet_url):
                df = self.sheet_connector.fetch_vocabulary_data()
                if not df.empty:
                    self.vocabulary_list = [
                        Word(
                            word=row['word'],
                            explanation=row['explanation'],
                            related_words=row['related_words'],
                            pos=row['pos'],
                            usage=row['usage'],
                            sentence=row['sentence']
                        ) for _, row in df.iterrows()
                    ]
                    return True
        return False
    
    def load_sample_vocabulary(self):
        """載入範例單字資料（用於測試）"""
        sample_data = [
            Word("aberrant", "偏離常軌的；異常的", "deviant, abnormal, atypical", "adj.", 
                 "用來形容行為或現象偏離正常標準", "His aberrant behavior worried his friends."),
            Word("abate", "減少；減輕", "diminish, subside, decrease", "v.", 
                 "通常指強度、數量或程度的減少", "The storm began to abate after midnight."),
            Word("abscond", "潛逃；逃匿", "flee, escape, run away", "v.", 
                 "秘密地或突然地離開以避免後果", "The thief absconded with the jewelry."),
            Word("abstemious", "節制的；節儉的", "temperate, moderate, restrained", "adj.", 
                 "在飲食或享樂方面自我克制", "Despite his wealth, he lived an abstemious lifestyle."),
            Word("admonish", "告誡；溫和地責備", "warn, caution, reprove", "v.", 
                 "以溫和但嚴肅的方式提醒或警告", "The teacher admonished the students for talking during the exam.")
        ]
        self.vocabulary_list = sample_data
    
    def get_random_word(self) -> Optional[Word]:
        """隨機選擇一個單字"""
        if self.vocabulary_list:
            return random.choice(self.vocabulary_list)
        return None
    
    def create_new_card(self, word: Word) -> VocabularyCard:
        """創建新的單字卡片"""
        return VocabularyCard(word)


class GREVocabularyApp:
    """GRE 單字學習應用程式主類別"""
    
    def __init__(self):
        self.vocab_manager = VocabularyManager()
        self.init_session_state()
    
    def init_session_state(self):
        """初始化 session state"""
        if 'current_card' not in st.session_state:
            st.session_state.current_card = None
        if 'vocabulary_loaded' not in st.session_state:
            st.session_state.vocabulary_loaded = False
        if 'vocabulary_list' not in st.session_state:
            st.session_state.vocabulary_list = []
    
    def render_header(self):
        """渲染應用程式標題"""
        st.markdown("""
        <div style="text-align: center; padding: 20px;">
            <h1 style="color: white; font-size: 3em;">📚 GRE 單字學習卡</h1>
        </div>
        """, unsafe_allow_html=True)
    
    def render_setup_section(self):
        """渲染設置區域"""
        st.sidebar.header("🔧 設置")
        
        # 選擇資料來源
        data_source = st.sidebar.radio(
            "選擇單字資料來源:",
            ["使用範例資料", "連接 Google Sheet"]
        )
        
        if data_source == "使用範例資料":
            if st.sidebar.button("載入範例單字", key="load_sample"):
                self.vocab_manager.load_sample_vocabulary()
                st.session_state.vocabulary_loaded = True
                st.sidebar.success("範例單字載入成功！")
        
        elif data_source == "連接 Google Sheet":
            st.sidebar.markdown("### Google Sheet 設置")
            
            # Sheet URL 輸入
            sheet_url = "https://docs.google.com/spreadsheets/d/1CVhtwrXiDoeEn9RFwu-swhmLS4LobDJpcm-CbEHutt4/edit?gid=0#gid=0"
            
            if st.sidebar.button("連接 Google Sheet", key="connect_sheet"):
                if sheet_url:
                    # 嘗試連接（使用 secrets.toml 中的憑證）
                    if self.vocab_manager.load_vocabulary_from_sheet(sheet_url):
                        st.session_state.vocabulary_loaded = True
                        st.sidebar.success(f"Google Sheet 連接成功！載入了 {len(st.session_state.vocabulary_list)} 個單字")
                    else:
                        st.sidebar.error("連接失敗，請檢查 Sheet URL 和 secrets.toml 設置")
                else:
                    st.sidebar.warning("請提供 Sheet URL")
            
            
    
    def render_study_section(self):
        """渲染學習區域"""
        if not st.session_state.vocabulary_loaded:
            st.info("請先在左側欄位載入單字資料")
            return
        
        if not st.session_state.vocabulary_list:
            st.error("沒有可用的單字資料")
            return
        
        # 顯示統計資訊
        st.markdown(f"""
        <div style="text-align: center; margin: 20px 0;">
            <span style="background: #E8F4FD; padding: 10px 20px; border-radius: 20px; color: #2E86AB;">
                📊 總共 {len(st.session_state.vocabulary_list)} 個單字
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        # 抽選新單字按鈕
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🎲 隨機抽選新單字", key="random_word", type="primary", use_container_width=True):
                word = self.vocab_manager.get_random_word()
                if word:
                    st.session_state.current_card = self.vocab_manager.create_new_card(word)
                    st.rerun()
        
        # 顯示單字卡片
        if st.session_state.current_card:
            self.render_vocabulary_card()
    
    def render_vocabulary_card(self):
        """渲染單字卡片"""
        card = st.session_state.current_card
        
        # 翻轉按鈕
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            button_text = "🔄 顯示中文釋義" if not card.is_flipped else "🔄 顯示英文"
            if st.button(button_text, key="flip_card", use_container_width=True):
                card.flip_card()
                st.rerun()
        
        # 顯示卡片內容
        if not card.is_flipped:
            card.render_front()
        else:
            card.render_back()
        
        # 學習進度提示
        st.markdown("""
        <div style="text-align: center; margin-top: 30px; color: #666;">
            💡 點擊翻轉按鈕查看釋義，點擊「隨機抽選新單字」繼續學習
        </div>
        """, unsafe_allow_html=True)
    
    def render_instructions(self):
        """渲染使用說明"""
        with st.expander("📖 使用說明"):
            st.markdown("""
            ### 如何使用這個 GRE 單字學習工具：
            
            #### 1. 設置資料來源
            - **範例資料**: 直接使用內建的範例單字開始學習
            - **Google Sheet**: 連接您自己的 Google Sheet 單字表
            
            #### 2. Google Sheet 設置步驟
            1. 創建 Google Service Account 並下載 JSON 憑證檔案
            2. 在 Google Sheet 中分享給 Service Account 的 email
            3. 確保您的 Sheet 包含以下欄位：
               - `word`: 英文單字
               - `explanation`: 中文釋義
               - `related_words`: 相關詞彙
               - `pos`: 詞性
               - `usage`: 用法說明
               - `sentence`: 例句
            
            #### 3. 開始學習
            - 點擊「隨機抽選新單字」開始
            - 先看英文，思考意思後點擊翻轉查看答案
            - 重複練習直到熟記所有單字
            
            #### 4. 學習建議
            - 建議每次學習 10-20 個單字
            - 多次複習已學過的單字
            - 注意相關詞彙和例句的使用
            """)
    
    def run(self):
        """運行應用程式"""
        st.set_page_config(
            page_title="GRE 單字學習卡",
            page_icon="📚",
            layout="wide"
        )
        
        # 渲染各個區域
        self.render_header()
        self.render_setup_section()
        self.render_study_section()
        self.render_instructions()
        
        # 頁腳
        st.markdown("""
        <div style="text-align: center; margin-top: 50px; color: #999; border-top: 1px solid #eee; padding-top: 20px;">
            Made with ❤️ using Streamlit | GRE 單字學習工具
        </div>
        """, unsafe_allow_html=True)


def main():
    """主函數"""
    app = GREVocabularyApp()
    app.run()


if __name__ == "__main__":
    main()