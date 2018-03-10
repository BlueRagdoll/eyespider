## talospider - item

#### 2.1.item

目标值提取类，当时是看[demiurge](https://github.com/matiasb/demiurge)这个项目研究了下`metaclass`，可以说item部分是参考这个的。

`item`的目的是是提取目标值，默认需要提供html或者对应的url才会返回自定义的field（写scrapy应该很清楚要先在item定义field吧），利用lxml解析。

就算没有爬虫模块，这个部分是可以单独使用的，目的时针对当爬取到目标页面那层的时候，进行目标数据的提取，当前目标数据的提取情况分两种：

##### 2.1.1.单页面单目标

比如这个网址http://book.qidian.com/info/1004608738

提取的对象很明确，这么多字段是一次结果，即一个页面一个目标，称之为单一目标获取，字段如下：

|        field        |     css_select     |
| :-----------------: | :----------------: |
|        title        |  .book-info>h1>em  |
|       author        |      a.writer      |
|        cover        |   a#bookImg>img    |
|      abstract       |  div.book-intro>p  |
|         tag         |     span.blue      |
|   latest_chapter    | div.detail>p.cf>a  |
| latest_chapter_time | div.detail>p.cf>em |

使用起来很简单：

```python
# -*- coding:utf-8 -*-
# !/usr/bin/env python
import time
from talospider import Item, TextField, AttrField
from pprint import pprint


class QidianItem(Item):
    title = TextField(css_select='.book-info>h1>em')
    author = TextField(css_select='a.writer')
    # 当提取的值是属性的时候，要定义AttrField
    cover = AttrField(css_select='a#bookImg>img', attr='src')
    abstract = TextField(css_select='div.book-intro>p')
    tag = TextField(css_select='span.blue')
    latest_chapter = TextField(css_select='li.update>div.detail>p.cf>a')
    latest_chapter_time = TextField(css_select='div.detail>p.cf>em')

    # 这里可以二次对获取的目标值进行处理，比如替换、清洗等
    def tal_title(self, title):
        # Clean your target value
        return title

    def tal_cover(self, cover):
        return 'http:' + cover

    # 当目标值的对象只有一个，默认将值提取出来，否则返回list，可以在这里定义一个函数进行循环提取
    def tal_tag(self, ele_tag):
        return '#'.join([i.text for i in ele_tag])

    def tal_latest_chapter_time(self, latest_chapter_time):
        return latest_chapter_time.replace(u'今天', str(time.strftime("%Y-%m-%d ", time.localtime()))).replace(u'昨日', str(
            time.strftime("%Y-%m-%d ", time.localtime(time.time() - 24 * 60 * 60))))


if __name__ == '__main__':
    # 获取值
    item_data = QidianItem.get_item(url='http://book.qidian.com/info/1004608738')
    pprint(item_data)
    # for python 2.7
    # import json
    # item_data = json.dumps(item_data, ensure_ascii=False)
    # print(item_data)

# output
{'abstract': '在破败中崛起，在寂灭中复苏。沧海成尘，雷电枯竭，那一缕幽雾又一次临近大地，世间的枷锁被打开了，一个全新的世界就此揭开神秘的一角……',
 'author': '辰东',
 'cover': 'http://qidian.qpic.cn/qdbimg/349573/1004608738/180',
 'latest_chapter': '第七百七十一章 神性粒子',
 'latest_chapter_time': '2017-11-22 22:57更新',
 'tag': '连载#签约#VIP',
 'title': '圣墟'}
```

写个类继承自Item就搞定了，ok

##### 2.1.2.单页面多目标

比如https://movie.douban.com/top250

这个页面每页展示25部电影，我的爬虫目标就是每页的25部电影信息，所以这个目标页的目标数据是多个item的，对于这种情况，目标是需要循环获取的。

我在`item`中限制了一点，当你定义的爬虫类需要在某一页面循环获取你的目标时，则需要定义`target_item`属性。

对于豆瓣250这个页面，我们的目标是25部电影信息，所以该这样定义：

|      field      |  css_select   |
| :-------------: | :-----------: |
| target_item（必须） |   div.item    |
|      title      |  span.title   |
|      cover      | div.pic>a>img |
|    abstract     |   span.inq    |



```python
# 定义继承自item的爬虫类
class DoubanSpider(Item):
    target_item = TextField(css_select='div.item')
    title = TextField(css_select='span.title')
    cover = AttrField(css_select='div.pic>a>img', attr='src')
    abstract = TextField(css_select='span.inq')

    def tal_title(self, title):
        if isinstance(title, str):
            return title
        else:
            return ''.join([i.text.strip().replace('\xa0', '') for i in title])

items_data = DoubanSpider.get_items(url='https://movie.douban.com/top250')
result = []
for item in items_data:
    result.append({
        'title': item.title,
        'cover': item.cover,
        'abstract': item.abstract,
    }
pprint(result)