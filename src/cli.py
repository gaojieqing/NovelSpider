from spiders.spider import ShuhaigeSpider, QQSpider, QisiSpider

if __name__ == '__main__':
    # spider = QQSpider()
    # spider.download(46557853)
    spider = ShuhaigeSpider()
    spider.download('236281')
