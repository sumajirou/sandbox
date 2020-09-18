from icrawler.builtin import BingImageCrawler


crawler = BingImageCrawler(storage={"root_dir": "dogs"})
crawler.crawl(keyword="犬", max_num=10)
