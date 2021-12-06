import os
import requests
from pyquery import PyQuery as pq
import genanki


MP3_PATH = "."
my_deck = genanki.Deck(
  2059400110,
  '潮汕话日常宝典')

my_model = genanki.Model(
  1091735104,
  'Simple Model with Media',
  fields=[
    {'name': 'Question'},
    {'name': 'Answer'},
    {'name': 'MyMedia1'},
    {'name': 'MyMedia2'},
  ],
  templates=[
    {
      'name': 'Card 1',
      'qfmt': '{{Question}}<br>{{MyMedia1}} <br> {{MyMedia2}}',
      'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
    },
  ])

my_package = genanki.Package(my_deck)


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
    #return os.path.join(MP3_PATH, outpath)
    return outpath

def check(word):
    """
    返回多个mp3保存地址
    """
    print(word)
    req = None
    mp3paths = []
    url = "http://www.czyzd.com/search?keyword={}"
    req = requests.get(url.format(word))
    d = pq(req.text)
    mean = ""
    for i in [1,2]:
        sel = '#list > dl > dd > ul > li:nth-child({})'.format(i)
        mean += " " + d(sel).text()
        sel = '#list > dl > dd > ul > li:nth-child({}) > button'.format(i)
        a = d(sel)
        if a.attr['data-rel']:
            r = requests.get(a.attr['data-rel'])
            path = '{}{}.mp3'.format(word, i)
            open(path, 'wb').write(r.content)
            mp3paths.append(path)
    return [mean, mp3paths]


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
                    print(e)
        if len(word['word']) == 1:
            continue
        mem[word['word']] = ["", []]
        for i in [0,1]:
            paths = []
            mean = ""
            for w in word['word']:
                if i > len(mem[w][1]) - 1:
                    break
                paths.append(mem[w][1][i])
                mean += mem[w][0]
            else:
                mem[word['word']][1].append(
                    merge(word['word']+str(i), paths))
                mem[word['word']][0] = mean

        if mem[word['word']][1]:
            print(mem[word['word']])
            voicePath1 = mem[word['word']][1][0]
            if len(mem[word['word']][1]) == 2:
                voicePath2 = mem[word['word']][1][1]
            else:
                voicePath2 = ""
            my_note = genanki.Note(model=my_model,
                fields=[word['word'], mem[word['word']][0],
                '[sound:{}]'.format(voicePath1),
                '[sound:{}]'.format(voicePath2),
                ])
            my_deck.add_note(my_note)
            for voicePath in mem[word['word']][1]:
                my_package.media_files.append(voicePath)

    my_package.write_to_file('Teachew.apkg')


if __name__ == '__main__':
    main()
