import os
import requests
from pyquery import PyQuery as pq


MP3_PATH = "mp3"


def check(word):
    """
    返回多个mp3保存地址
    """
    url = "http://www.czyzd.com/search?keyword={}"
    r = requests.get(url.format(word))
    d = pq(r.text)
    ret = []
    for i in [1,2]:
        sel = '#list > dl > dd > ul > li:nth-child({}) > button'.format(i)
        a = d(sel)
        if a.attr['data-rel']:
            r = requests.get(a.attr['data-rel'])
            path = '{}/{}-{}.mp3'.format(MP3_PATH, word, i)
            open(path, 'wb').write(r.content)
            ret.append(path)
    return ret


def main():
    os.makedirs(MP3_PATH)
    mp3_paths = check('姐')


if __name__ == '__main__':
    main()