#記事全文を要約する関数
def sum_text(document):
    from pysummarization.nlpbase.auto_abstractor import AutoAbstractor
    from pysummarization.tokenizabledoc.mecab_tokenizer import MeCabTokenizer
    from pysummarization.abstractabledoc.top_n_rank_abstractor import TopNRankAbstractor

    auto_abstractor = AutoAbstractor()
    auto_abstractor.tokenizable_doc = MeCabTokenizer()
    auto_abstractor.delimiter_list = ["。", "\n"]
    abstractable_doc = TopNRankAbstractor()
    result_dict = auto_abstractor.summarize(document, abstractable_doc)

    return ''.join(result_dict["summarize_result"])

if __name__ == '__main__':
    import re
    import requests
    from bs4 import BeautifulSoup
    import time
    import os
    import pandas as pd
    import codecs
    import sys
    from urllib.parse import urljoin
    from django.utils.html import strip_tags

    #「←Older Posts」ボタンと「Newer Posts」ボタン用にフラグを設定
    flag = 1
    df = pd.DataFrame()
    #csvファイルの保存名.例ではカレントディレクトリに出力する
    save_csv = './aws_pandas_normal.csv'

    base_url="https://aws.amazon.com/jp/blogs/news/"
    #後述．ページ遷移用のURLを保持する変数
    dynamic_url="https://aws.amazon.com/jp/blogs/news/"
    #csvに出力するカラムを設定
    data_col = ["information1", "information2", "information3"]

    #取得ページ分ループする.例では3ページ分取得する
    for _ in range(3):
        res = requests.get(dynamic_url)
        res.raise_for_status()

        html = BeautifulSoup(res.text, 'lxml')
        detail_url_list = html.find_all("section")

        #「←Older Posts」ボタンと「Newer Posts→」ボタンのリンクから次ページへのリンクを取得する
        #最初のページでは「←Older Posts」ボタンから次ページのリンクを取得する
        #2ページ目以降では末尾から2つ目にある「←Older Posts」ボタンから次ページのリンクを取得する
        #2ページ目以降では「Newer Posts→」ボタンが最後尾になる 例: (blog-btn-a)[-1]
        next_page = html.find_all("a",attrs={"class": "blog-btn-a"})[-1].get("href") if flag==1 else html.find_all("a",attrs={"class": "blog-btn-a"})[-2].get("href")
        flag = 0

        #ページ内の記事数分ループする
        #例： AWS公式ブログでは1ページに10記事あるため，10回ループする．
        for i in range(len(detail_url_list)):
            #取得記事を設定
            res2 = requests.get(urljoin(base_url, detail_url_list[i].a.get("href")))
            res2.raise_for_status()
            #取得記事を解析
            html2 = BeautifulSoup(res2.text, 'lxml')

            # 抜き出す情報に合わせて抽出するタグの変更
            #タイトル
            information1 = html2.title.string
            #本文
            information2 = html2.find_all('p')
            #htmlタグ除去
            information2 = strip_tags(information2)
            #文章を要約
            information2 = sum_text(information2)
            #不要な改行 括弧[] カンマを取り除く
            #reを使って改修したい
            information2 = information2.replace('\n','')
            information2 = information2.replace('[','')
            information2 = information2.replace(']','')
            information2 = information2.replace(',','')
            #発行日付
            information3 = html2.find_all('time')
            #htmlタグ除去
            information3 = strip_tags(information3)
            #不要な改行 括弧[] カンマを取り除く
            #reを使って改修したい
            information3 = information3.replace('[','')
            information3 = information3.replace(']','')
            information3 = information3.replace(',','')

            #csvファイルへ出力
            s = pd.Series([information3, information1, information2],index=data_col)
            df = df.append(s, ignore_index=True)
            df.to_csv(save_csv)

            #sleep処理(WEBサーバに負荷をかけないため)
            print(str(len(df)) + "記事を取得しました。2秒待機します。")
            time.sleep(2)

        #最終ページのとき終了
        if bool(next_page) == False:
            break

        #次のページにURLを設定する
        #2ページ目の場合
        # dynamic_url = (~/news/) + (~/news/page/2/)
        # dynamic_url = ~/news/page/2/
        dynamic_url = urljoin(base_url, next_page)
