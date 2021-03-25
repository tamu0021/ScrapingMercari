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
            print(str(page) + "ページ取得中")
            
            # 商品ごとに名前と値段、購入済みかどうか取得
            for post in posts:
                # 商品名
                title = post.find_elements_by_css_selector(PRODUCT_NAME).text
                # 値段
                price = post.find_elements_by_css_selector(PRODUCTS_PRICE).text
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
                series = pd.Series([title, price, sold, Url], columns)
                data_frame = data_frame.append(series, columns)
                    
            # 次ページへ
            page += 1
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
    print("Finish!)
            
            
            
