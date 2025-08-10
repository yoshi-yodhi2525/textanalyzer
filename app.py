import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
from wordcloud import WordCloud
import re
import jieba
import emoji
from collections import Counter
import networkx as nx
from datetime import datetime
import numpy as np
from textblob import TextBlob
import warnings
warnings.filterwarnings('ignore')

# フォント設定のインポート
from fonts import get_japanese_font_path, get_font_family

# Matplotlibのフォント設定
font_path = get_japanese_font_path()
if font_path:
    # フォントファイルをMatplotlibに登録
    font_prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = font_prop.get_name()
    # フォールバックフォントの設定
    plt.rcParams['font.sans-serif'] = ['Noto Sans JP', 'DejaVu Sans', 'sans-serif']
    plt.rcParams['axes.unicode_minus'] = False

# ページ設定
st.set_page_config(
    page_title="X投稿分析アプリ",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# タイトルと説明
st.title("📊 X投稿分析アプリ")
st.markdown("CSVファイルをアップロードして、Xの投稿を分析しましょう！")

# サイドバー
st.sidebar.header("📁 データアップロード")
uploaded_file = st.sidebar.file_uploader(
    "CSVファイルを選択してください",
    type=['csv'],
    help="投稿日時とテキストの列を含むCSVファイルをアップロードしてください"
)

# ハッシュタグ検索
st.sidebar.header("🔍 ハッシュタグ検索")
search_hashtag = st.sidebar.text_input(
    "分析したいハッシュタグを入力",
    placeholder="#ノンプロ研",
    help="特定のハッシュタグに関する投稿のみを分析します"
)

# データ読み込みと前処理
@st.cache_data
def load_and_process_data(file):
    """CSVファイルを読み込んで前処理を行う"""
    try:
        df = pd.read_csv(file)
        
        # 列名の正規化
        df.columns = df.columns.str.strip()
        
        # 投稿日時の処理
        if '投稿日時' in df.columns:
            df['投稿日時'] = pd.to_datetime(df['投稿日時'], format='%Y/%m/%d %H:%M', errors='coerce')
        elif 'created_at' in df.columns:
            df['投稿日時'] = pd.to_datetime(df['created_at'], errors='coerce')
        
        # テキスト列の確認
        text_column = None
        for col in ['テキスト', 'text', 'content', 'tweet_text']:
            if col in df.columns:
                text_column = col
                break
        
        if text_column is None:
            st.error("テキスト列が見つかりません。CSVファイルに'テキスト'列があることを確認してください。")
            return None
        
        # テキストの前処理
        df['テキスト_処理済み'] = df[text_column].astype(str).apply(preprocess_text)
        
        # ハッシュタグの抽出
        df['ハッシュタグ'] = df[text_column].astype(str).apply(extract_hashtags)
        
        # 感情分析
        df['感情スコア'] = df[text_column].astype(str).apply(analyze_sentiment)
        
        return df, text_column
        
    except Exception as e:
        st.error(f"ファイルの読み込みエラー: {str(e)}")
        return None, None

def preprocess_text(text):
    """テキストの前処理"""
    if pd.isna(text):
        return ""
    
    # URLの除去
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', str(text))
    
    # メンションの除去
    text = re.sub(r'@\w+', '', text)
    
    # 絵文字の除去
    text = emoji.replace_emoji(text, replace='')
    
    # 特殊文字の除去
    text = re.sub(r'[^\w\s#]', ' ', text)
    
    # 複数の空白を単一の空白に
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def extract_hashtags(text):
    """ハッシュタグを抽出"""
    if pd.isna(text):
        return []
    hashtags = re.findall(r'#\w+', str(text))
    return hashtags

def analyze_sentiment(text):
    """感情分析（簡易版）"""
    if pd.isna(text) or text == "":
        return 0
    
    try:
        blob = TextBlob(text)
        return blob.sentiment.polarity
    except:
        return 0

def filter_by_hashtag(df, hashtag):
    """特定のハッシュタグでフィルタリング"""
    if not hashtag or hashtag == "":
        return df
    
    hashtag = hashtag.lower()
    filtered_df = df[df['テキスト_処理済み'].str.contains(hashtag, case=False, na=False)]
    
    if len(filtered_df) == 0:
        # ハッシュタグ列で検索
        filtered_df = df[df['ハッシュタグ'].apply(lambda x: any(hashtag in tag.lower() for tag in x))]
    
    return filtered_df

# メイン処理
if uploaded_file is not None:
    df, text_column = load_and_process_data(uploaded_file)
    
    if df is not None:
        st.success(f"✅ データの読み込みが完了しました！ ({len(df)}件の投稿)")
        
        # ハッシュタグでフィルタリング
        if search_hashtag:
            df_filtered = filter_by_hashtag(df, search_hashtag)
            st.info(f"🔍 '{search_hashtag}' に関する投稿: {len(df_filtered)}件")
        else:
            df_filtered = df
            st.info("🔍 全投稿を分析対象としています")
        
        if len(df_filtered) > 0:
            # タブを作成
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📈 基本統計", 
                "🏆 ランキング", 
                "☁️ ワードクラウド", 
                "🗺️ 単語マップ", 
                "📅 時系列分析"
            ])
            
            with tab1:
                st.header("📊 基本統計")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("総投稿数", len(df_filtered))
                
                with col2:
                    avg_length = df_filtered['テキスト_処理済み'].str.len().mean()
                    st.metric("平均文字数", f"{avg_length:.1f}")
                
                with col3:
                    total_hashtags = sum(len(hashtags) for hashtags in df_filtered['ハッシュタグ'])
                    st.metric("総ハッシュタグ数", total_hashtags)
                
                with col4:
                    avg_sentiment = df_filtered['感情スコア'].mean()
                    st.metric("平均感情スコア", f"{avg_sentiment:.3f}")
                
                # データプレビュー
                st.subheader("📋 データプレビュー")
                st.dataframe(
                    df_filtered[['投稿日時', 'テキスト_処理済み', 'ハッシュタグ', '感情スコア']].head(10),
                    use_container_width=True
                )
            
            with tab2:
                st.header("🏆 ランキング分析")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📊 ハッシュタグランキング")
                    all_hashtags = []
                    for hashtags in df_filtered['ハッシュタグ']:
                        all_hashtags.extend(hashtags)
                    
                    hashtag_counts = Counter(all_hashtags)
                    top_hashtags = dict(hashtag_counts.most_common(10))
                    
                    if top_hashtags:
                        fig = px.bar(
                            x=list(top_hashtags.values()),
                            y=list(top_hashtags.keys()),
                            orientation='h',
                            title="ハッシュタグ使用頻度トップ10"
                        )
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("ハッシュタグが見つかりませんでした")
                
                with col2:
                    st.subheader("📊 感情スコアランキング")
                    sentiment_df = df_filtered.nlargest(10, '感情スコア')[['テキスト_処理済み', '感情スコア']]
                    
                    if not sentiment_df.empty:
                        fig = px.bar(
                            x=sentiment_df['感情スコア'],
                            y=sentiment_df['テキスト_処理済み'].str[:30] + "...",
                            orientation='h',
                            title="感情スコア上位10件"
                        )
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("感情スコアのデータがありません")
            
            with tab3:
                st.header("☁️ ワードクラウド")
                
                # 全テキストを結合
                all_text = ' '.join(df_filtered['テキスト_処理済み'].dropna())
                
                if all_text.strip():
                    # 日本語の分かち書き
                    words = jieba.cut(all_text)
                    word_text = ' '.join(words)
                    
                    # 日本語フォントの設定
                    font_path = get_japanese_font_path()
                    
                    # ワードクラウドの生成
                    wordcloud = WordCloud(
                        width=800,
                        height=400,
                        background_color='white',
                        max_words=100,
                        colormap='viridis',
                        font_path=font_path if font_path else None
                    ).generate(word_text)
                    
                    # 表示
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.imshow(wordcloud, interpolation='bilinear')
                    ax.axis('off')
                    st.pyplot(fig)
                    
                    # 単語頻度の棒グラフ
                    word_counts = Counter(word_text.split())
                    top_words = dict(word_counts.most_common(20))
                    
                    fig = px.bar(
                        x=list(top_words.values()),
                        y=list(top_words.keys()),
                        orientation='h',
                        title="単語出現頻度トップ20"
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("テキストデータがありません")
            
            with tab4:
                st.header("🗺️ 単語マップ（共起ネットワーク）")
                
                # 共起ネットワークの作成
                if len(df_filtered) > 0:
                    # 単語の共起を計算
                    word_pairs = []
                    for text in df_filtered['テキスト_処理済み'].dropna():
                        words = jieba.cut(text)
                        words = [w for w in words if len(w) > 1]  # 1文字の単語を除外
                        for i in range(len(words)):
                            for j in range(i+1, min(i+3, len(words))):  # 隣接する単語のみ
                                word_pairs.append(tuple(sorted([words[i], words[j]])))
                    
                    if word_pairs:
                        pair_counts = Counter(word_pairs)
                        top_pairs = pair_counts.most_common(20)
                        
                        # ネットワークグラフの作成
                        G = nx.Graph()
                        for (word1, word2), weight in top_pairs:
                            G.add_edge(word1, word2, weight=weight)
                        
                        # ノードの位置を計算
                        pos = nx.spring_layout(G, k=1, iterations=50)
                        
                        # プロット
                        fig, ax = plt.subplots(figsize=(12, 8))
                        # 日本語フォントの設定
                        font_path = get_japanese_font_path()
                        if font_path:
                            font_prop = fm.FontProperties(fname=font_path)
                        else:
                            font_prop = fm.FontProperties()
                        
                        nx.draw(
                            G, pos,
                            with_labels=True,
                            node_color='lightblue',
                            node_size=[G.degree(node) * 100 for node in G.nodes()],
                            font_size=8,
                            font_family=font_prop.get_name(),
                            edge_color='gray',
                            width=[G[u][v]['weight'] / 2 for u, v in G.edges()]
                        )
                        plt.title("単語共起ネットワーク", fontsize=14)
                        st.pyplot(fig)
                        
                        # 共起頻度の表
                        st.subheader("共起頻度上位20件")
                        cooccurrence_df = pd.DataFrame(
                            [(w1, w2, count) for (w1, w2), count in top_pairs],
                            columns=['単語1', '単語2', '共起回数']
                        )
                        st.dataframe(cooccurrence_df, use_container_width=True)
                    else:
                        st.info("共起データが不足しています")
                else:
                    st.info("データが不足しています")
            
            with tab5:
                st.header("📅 時系列分析")
                
                if '投稿日時' in df_filtered.columns and not df_filtered['投稿日時'].isna().all():
                    # 日付別投稿数
                    daily_posts = df_filtered.groupby(df_filtered['投稿日時'].dt.date).size().reset_index()
                    daily_posts.columns = ['日付', '投稿数']
                    
                    fig = px.line(
                        daily_posts,
                        x='日付',
                        y='投稿数',
                        title="日別投稿数推移"
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # 時間別投稿数
                    hourly_posts = df_filtered.groupby(df_filtered['投稿日時'].dt.hour).size().reset_index()
                    hourly_posts.columns = ['時間', '投稿数']
                    
                    fig = px.bar(
                        hourly_posts,
                        x='時間',
                        y='投稿数',
                        title="時間別投稿数分布"
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # 感情スコアの時系列推移
                    if '感情スコア' in df_filtered.columns:
                        sentiment_time = df_filtered.groupby(df_filtered['投稿日時'].dt.date)['感情スコア'].mean().reset_index()
                        sentiment_time.columns = ['日付', '平均感情スコア']
                        
                        fig = px.line(
                            sentiment_time,
                            x='日付',
                            y='平均感情スコア',
                            title="日別平均感情スコア推移"
                        )
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("投稿日時のデータが不足しています")
        else:
            st.warning("フィルタリング条件に一致する投稿が見つかりませんでした。")
    
else:
    st.info("👆 サイドバーからCSVファイルをアップロードしてください")
    
    # サンプルデータの説明
    st.markdown("""
    ### 📋 対応しているCSV形式
    
    以下の列を含むCSVファイルに対応しています：
    - **投稿日時**: 投稿の日時（例：2025/08/09 21:27）
    - **テキスト**: 投稿の内容
    
    ### 🔍 分析機能
    
    1. **基本統計**: 投稿数、平均文字数、ハッシュタグ数など
    2. **ランキング**: ハッシュタグ使用頻度、感情スコアランキング
    3. **ワードクラウド**: 頻出単語の可視化
    4. **単語マップ**: 単語の共起関係をネットワークで表示
    5. **時系列分析**: 投稿数の推移、時間分布、感情スコアの変化
    
    ### 💡 使い方
    
    1. CSVファイルをアップロード
    2. 分析したいハッシュタグを入力（オプション）
    3. 各タブで分析結果を確認
    """)

# フッター
st.markdown("---")
st.markdown("📊 X投稿分析アプリ | Streamlit Cloud対応")
