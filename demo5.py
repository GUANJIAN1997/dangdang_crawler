import requests
from lxml import etree
import pymongo
from pymongo.collection import Collection

class Dangdang(object):
    mongo_client = pymongo.MongoClient(host="127.0.0.1", port=27017)
    # 指定数据库为dangdang_db
    dangdang_db = mongo_client["dangdang_db"]
    def __init__(self):
        self.header = {
            "Host": "bang.dangdang.com",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        self.dangdang = Collection(Dangdang.dangdang_db, "dangdang")

    def get_dangdang(self, page):
        url = "http://bang.dangdang.com/books/fivestars/01.00.00.00.00.00-recent30-0-0-1-%s" % page
        # 发送请求
        response = requests.get(url=url, headers=self.header)
        if response:
            # html数据的实例化 
            html = etree.HTML(response.text)
            items = html.xpath("//ul[@class='bang_list clearfix bang_list_mode']/li")
            return items

    def join_list(self, item):
        """处理列表到字符串"""
        return "".join(item)

    def parse_item(self, items):
        # 解析具体的图书条目
        # 适用于存放存储到mongodb之前的数据
        result_list = []
        for item in items:
            # 图书的名称
            title = item.xpath(".//div[@class='name']/a/text()")
            # 图书评论
            comment = item.xpath(".//div[@class='star']/a/text()")
            # 推荐信息
            recommend = item.xpath(".//div[@class='star']/span[@class='tuijian']/text()")
            # 作者信息
            author = item.xpath(".//div[@class='publisher_info'][1]/a[1]/@title")
            # 出版时间
            publication_time = item.xpath(".//div[@class='publisher_info'][2]/span/text()")
            # 出版社
            press = item.xpath(".//div[@class='publisher_info'][2]/a/text()")
            # 五星评分
            score = item.xpath(".//div[@class='biaosheng']//text()")
            # 价格
            price = item.xpath(".//div[@class='price']/p[1]/span[1]/text()")
            # 折扣
            discount = item.xpath(".//div[@class='price']/p/span[@class='price_s']/text()")
            # 电子书价格
            e_book = item.xpath(".//div[@class='price']/p[@class='price_e']/span[@class='price_n']/text()")
            result_list.append({
                    "title": self.join_list(title),
                    "comment": self.join_list(comment),
                    "recommend": self.join_list(recommend),
                    "author": self.join_list(author),
                    "publication_time": self.join_list(publication_time),
                    "press": self.join_list(press),
                    "score": self.join_list(score),
                    "price": self.join_list(price),
                    "discount": self.join_list(discount),
                    "e_booke": self.join_list(e_book)
                })
        return result_list

    def insert_data(self, result_list):
        """插入数据到mongodb"""
        self.dangdang.insert_many(result_list)


def main():
    import json
    d = Dangdang()
    for page in range(1,26):
        items = d.get_dangdang(page=page)
        result = d.parse_item(items=items)
        d.insert_data(result)

if __name__ == '__main__':
        main()
