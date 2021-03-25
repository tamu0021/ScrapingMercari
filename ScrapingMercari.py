import os
# csvファイルを扱う
import pandas as pd
import csv
# Chromeからメルカリを開く
from selenium import webdriver
# 待ち時間
import time
# 点描する。
import matplotlib.pyplot as plt

# メルカリ起動のための待ち時間
SLEEP_TIME_FOR_RUN_MERCARI = 5
# 商品ごとのHTMLを取得するための変数
# 商品情報全体
PRODUCTS_INFORMATION = ".items-box"
# 商品名
PRODUCT_NAME = "h3.items-box-name"
# 商品の値段
PRODUCT_PRICE = ".items-box-price"
# 商品購入済みのステータス
PRODUCT_SOLDOUT_STARUS = ".item-sold-out-badge"
# 次ページのURL
NEXT_PAGE_URL = "li.pager-next .pager-cell a"
# パーセントの単位変換を行うための定数
BASE_PERCENT = 100

def search_mercari(search_words):
    # 検索ワードをそのままディレクトリ名とするため、一時退避する。
    search_words_alt = search_words

    # 検索ワードが複数ある場合、and演算するために「+」で連結するよう整形する。
    words = search_words.split("_")
    search_words = words[0]
    for i in range(1, len(words)):
        search_words = search_words + "+" + words[i]

    # メルカリで検索するためのURL
    mercari_url = "https://www.mercari.com/jp/search/?keyword=" + search_words

    # ブラウザを開く
    # 本pythonファイルと同ディレクトリにchromedriver.exeがある場合、
    # 引数は空でも良い。
    # また、chromedriverとPCのchromeのバージョンに注意。
    # ここに矛盾があるとエラーが発生する。
    browser = webdriver.Chrome()
    
    # メルカリの起動を待つ
    sleep_time(SLEEP_TIME_FOR_RUN_MERCARI)
    
    # 表示ページ
    display_page = 1
    # 気になるリストを作成
    columns = ["Name", "Price", "Sold", "Url"]
    # 配列名を指定
    data_frame = pd.DataFrame(columns=columns)
    
    # 処理内容
    try:
        while(True):
            # ブラウザで検索
            browser.get(mercari_url)
            # 商品ごとのHTMLを全取得
            posts = browser.find_elements_by_css_selector(PRODUCTS_INFORMATION)
            # 何ページ目を取得しているか表示
            print(str(display_page) + "ページ取得中")
            
            # 商品ごとに名前と値段、購入済みかどうか取得
            for post in posts:
                # 商品名
                title = post.find_elements_by_css_selector(PRODUCT_NAME).text
                # 値段
                price = post.find_elements_by_css_selector(PRODUCT_PRICE).text
                # 値段中に不要な文字があるので消去
                price = price.replace("\\", "")
                price = price.replace(".", "")
                
                # 売り切れているかどうかのステータス。売り切れはTrue、まだ売り切れでなければFalse
                soldout_sts = False
                if (len(post.find_elements_by_css_selector(PRODUCT_SOLDOUT_STARUS)) > 0):
                    soldout_sts = True
                                      
                # 商品のURLを取得
                product_url = post.find_elements_by_css_selector("a").get_attribute("href")
                
                # スクレイピングした情報をリストに追加
                series = pd.Series([title, price, soldout_sts, product_url], columns)
                data_frame = data_frame.append(series, columns)
                    
            # 次ページへ
            display_page += 1
            # 次ページに進むためのURKを取得
            mercari_url = browser.find_elements_by_css_selector(NEXT_PAGE_URL).get_attribute("href")
            # 次ページに進んでるよ、という事を表示
            print("Moving to next page ...")
    except:
        # 全ページ完了後、例外が飛んでくる。
        print("Next page is nothing.")
        
    # 最後に得たデータをCSVとして保存
    filename = "mercari_scraping_" + search_words_alt + ".csv"
    data_frame.to_csv(search_words_alt + "/" + filename, encoding="utf-8-sig")
    print("Finish!")
            
def make_graph(search_words, except_words, max_price, graph_width):
    # CSV ファイルを開く
    data_frame = pd.read_csv(search_words + "/" +
                     "mercari_scraping_" + search_words + ".csv")

    # "Name"に"except_words"が入っているものを除く
    if(len(except_words) != 0):
        exc_words = except_words.split("_")
        for i in range(len(exc_words)):
            data_frame = data_frame[data_frame["Name"].str.contains(exc_words[i]) == False]
    else:
        pass

    # 購入済みの商品だけを表示
    display_soldout_product = data_frame[data_frame["Sold"] == 1]

    # 価格(Price)が1500円以下の商品のみを表示
    display_soldout_product = display_soldout_product[display_soldout_product["Price"] < max_price]

    # カラム名を指定「値段」「その値段での個数」「パーセント」の3つ
    columns = ["Price",  "Num", "Percent"]

    # 配列名を指定する
    all_num = len(display_soldout_product)
    num = 0
    data_frame_percent = pd.DataFrame(columns=columns)

    for i in range(int(max_price/graph_width)):

        # 少し余分にグラフ幅をとる。
        MIN = i * graph_width - 1
        MAX = (i + 1) * graph_width

        # MINとMAXの値の間にあるものだけをリストにして、len()を用いて個数を取得
        data_frame_list = display_soldout_product[display_soldout_product["Price"] > MIN]
        data_frame_list = data_frame_list[data_frame_list["Price"] < MAX]
        num_of_sold_out_product = len(data_frame_list)

        # 累積にしたいので、numに今回の個数を足していく
        num += num_of_sold_out_product

        # ここでパーセントを計算する
        percent = num / all_num * BASE_PERCENT

        # 値段はMINとMAXの中央値とした
        price = (MIN + MAX + 1) / 2
        series = pd.Series([price, num, percent], columns)
        data_frame_percent = data_frame_percent.append(series, columns)

    # CSVに保存
    filename = "mercari_histgram_" + search_words + ".csv"
    data_frame_percent.to_csv(search_words + "/" + filename, encoding="utf-8-sig")

    # グラフの描画
    """
    :param kind: グラフの種類を指定
    :param y: y 軸の値を指定
    :param graph_width: グラフ幅を指定 
    :param alpha: グラフの透明度(0:透明 ~ 1:濃い)
    :param figsize: グラフの大きさを指定
    :param color: グラフの色
    :param secondary_y: 2 軸使用の指定(Trueの場合)
    """
    ax1 = display_soldout_product.plot(kind="hist", y="Price", graph_width=25,
                      secondary_y=True, alpha=0.9)
    data_frame_percent.plot(kind="area", x="Price", y=[
        "Percent"], alpha=0.5, ax=ax1, figsize=(20, 10), color="k")
    plt.savefig(search_words + "/" + "mercari_histgram_" +
                search_words + ".jpg")

           
            
