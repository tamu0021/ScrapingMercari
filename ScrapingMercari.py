# Chromeからメルカリを開く
from selenium import webdriver
# 待ち時間
import time

load_url = "https://www.mercari.com/jp/search/?keyword=パソコン+中古"
sleep_time = 5
# Chromeを使ってURLを開く。
browser = webdriver.Chrome()
# 時間がかかるため、待ち時間を入れる。
time.sleep(sleep_time)
# ブラウザで検索
browser.get(load_url)
# 商品ごとのHTMLを全取得
posts = browser.find_elements_by_css_selector(".items-box")
# HTML全体の表示
print(posts)