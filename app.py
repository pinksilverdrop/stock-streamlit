import altair as alt
import pandas as pd
import streamlit as st
import yfinance as yf


st.title('米国株価可視化アプリ')

st.sidebar.write("""
# GAFA株価
こちらは株価可視化ツールです。以下のオプションから表示日数を指定できます。
""")

st.sidebar.write("""
## 表示日数選択
""")
days = st.sidebar.slider('日数', 1, 50, 20)

st.write(f"""
### 過去 **{days}** 日間のGAFA株価
""")


@st.cache
def get_data(days, tickers):
    """
    指定した日数文の過去の株価をDataFrameで返す
    Parameters
    ---------------
        days(int): 日数
        tickers(dict): 会社名とティッカーを格納した
    Returns
    ---------------
        株価 ('Company', 'Close')
    """
    dfs = []
    for company, ticker in tickers.items():
        tkr = yf.Ticker(ticker)
        hist = tkr.history(period=f'{days}d')
        hist.index = hist.index.strftime('%d %B %Y')
        hist = hist[['Close']]
        hist.columns = [company]
        hist = hist.T
        hist.index.name = 'Name'
        dfs.append(hist)
    return pd.concat(dfs)

try:
    st.sidebar.write("""
    ## 株価の範囲指定
    """)
    ymin, ymax = st.sidebar.slider(
        '範囲を指定してください',
        0.0, 3500.0, (0.0, 3500.0)
    )

    tickers = {
        'apple': 'AAPL',
        'facebook': 'FB',
        'google': 'GOOGL',
        'microsoft': 'MSFT',
        'netflix': 'NFLX',
        'amazon': 'AMZN'
    }

    df = get_data(days, tickers)

    companies = st.multiselect(
        '会社名を選択してください。',
        list(df.index),
        ['google', 'amazon', 'facebook', 'apple']
    )
    if not companies:
        st.error('少なくとも一社は選んでください。')
    else:
        data = df.loc[companies]
        st.write("### 株価(USD)", data.sort_index())

        data = data.T.reset_index()
        data = pd.melt(data, id_vars=['Date']).rename(
            columns={'value': 'Stock Prices(USD)'}
        )

        chart = (
            alt.Chart(data).mark_line(opacity=0.8, clip=True).encode(
                x="Date:T",
                y=alt.Y("Stock Prices(USD):Q", stack=None, scale=alt.Scale(domain=[ymin, ymax])),
                color='Name:N'
            )
        )
        st.altair_chart(chart, use_container_width=True)

except:
    st.error(
        "予期せぬエラーが発生しました。"
    )
