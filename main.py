import os
import requests
from pyquery import PyQuery as pq


MP3_PATH = "mp3"


def getWords():
    with open('./dict.txt', 'r') as f:
        for line in f:
            tmp = line.split()
            info = {}
            info['word'] = tmp[0]
            if len(tmp) > 2:
                info['mean'] = tmp[-1]
            yield info 

def merge(word, paths):
    outpath = '{}.mp3'.format(word)
    cmd = 'cd {} && test -f {} || ffmpeg -i "concat:{}" -acodec copy {}'\
        .format(MP3_PATH, outpath, '|'.join([os.path.basename(p) for p in paths]), outpath)
    os.system(cmd)
    return os.path.join(MP3_PATH, outpath)

def check(word):
    """
    返回多个mp3保存地址
    """
    print(word)
    url = "http://www.czyzd.com/search?keyword={}"
    r = requests.get(url.format(word))
    d = pq(r.text)
    ret = []
    for i in [1,2]:
        path = '{}/{}{}.mp3'.format(MP3_PATH, word, i)
        if not os.path.exists(path):
            sel = '#list > dl > dd > ul > li:nth-child({}) > button'.format(i)
            a = d(sel)
            if a.attr['data-rel']:
                r = requests.get(a.attr['data-rel'])
                open(path, 'wb').write(r.content)
                ret.append(path)
    return ret

def main():
    os.makedirs(MP3_PATH, exist_ok=True)
    mem = {}
    for word in getWords():
        for w in word['word']:
            if w not in mem:
                try:
                    mem[w] = check(w)
                    print(mem[w])
                except Exception as e:
                    pass
        if len(word['word']) == 1:
            continue
        mem[word['word']] = []
        for i in [0,1]:
            paths = []
            for w in word['word']:
                if i > len(mem[w]) - 1:
                    break
                paths.append(mem[w][i])
            else:
                mem[word['word']].append(
                    merge(word['word']+str(i), paths))

if __name__ == '__main__':
    main()