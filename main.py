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
    ret = []
    req = None
    find_one = False
    for i in [1,2]:
        path = '{}{}.mp3'.format(word, i)
        if not os.path.exists(path):
            print(path)
            if find_one:
                continue
            url = "http://www.czyzd.com/search?keyword={}"
            if req is None:
                req = requests.get(url.format(word))
            d = pq(req.text)
            sel = '#list > dl > dd > ul > li:nth-child({}) > button'.format(i)
            a = d(sel)
            if a.attr['data-rel']:
                r = requests.get(a.attr['data-rel'])
                open(path, 'wb').write(r.content)
                ret.append(path)
        else:
            find_one = True
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
        if mem[word['word']]:
            voicePath1 = mem[word['word']][0]
            if len(mem[word['word']]) == 2:
                voicePath2 = mem[word['word']][1]
            else:
                voicePath2 = ""
            my_note = genanki.Note(model=my_model,
                fields=[word['word'], word['mean'], 
                '[sound:{}]'.format(voicePath1),
                '[sound:{}]'.format(voicePath2),
                ])
            my_deck.add_note(my_note)
            for voicePath in mem[word['word']]:
                my_package.media_files.append(voicePath)
    
    my_package.write_to_file('Teachew.apkg')


if __name__ == '__main__':
    main()