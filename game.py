import requests
import random
import json
import sys
import os
import time

base_file = 'base_q.json'
sectors = ['100','100',
            '200','200',
            '300','300',
            '400','x3',
            '500','x0',
            'x2',
            'propusk','100',
            '200','300',
            '400','propusk','x2',
            'open',
        ]

scores = {}


def download_from_imho24():
    print('Попытка скачать с сайта https://imho24.info/')
    try:
        from bs4 import BeautifulSoup as bs
    except Exception as e:
        print('Ошибка импорта пакета bs4, "pip install bs4" please', e)
        return False
    faq = {}
    url = 'https://imho24.info/answers/hobbies/detail/914/'
    need_class = 'catalog-element'
    resp = requests.get(url)
    soup = bs(resp.text, 'html.parser')
    content = soup.findAll('div', class_=need_class)
    lq = str(content[0]).split('<br/>')[9:-2]
    lq = [x.strip(' ') for x in lq if len(x) > 2]
    faq = dict([(i, [lq[i], lq[i+1]]) for i in range(0, len(lq), 2)])
    return faq


def get_urls_from_pcho():
    '''
    получение ссылок на вопросы и ответы с сайта https://polechudes-otvet.ru/
    return list href
    '''
    try:
        from bs4 import BeautifulSoup as bs
    except Exception as e:
        print('Ошибка импорта пакета bs4, "pip install bs4" please', e)
        return False
    # pages = ('li', class_='previous').<a href>
    url = 'https://polechudes-otvet.ru/'
    index = 1
    all_urls_of_questions = []
    index = 0
    while True:
        if index > 10:
            break
        resp = requests.get(url)
        if resp.status_code != 200:
            break
        print(resp.status_code)
        soup = bs(resp.text, 'html.parser')
        trs = soup.findAll('tr')

        for tr in trs:
            a = tr.find('a')
            if not a:
                continue
            if a.text.lower() != 'установить игру':
                all_urls_of_questions.append(a.attrs['href'])
        index += 1
        li = soup.find('li', class_='previous')
        if not li:
            break
        url = li.find('a').attrs['href']
        index += 1
    return all_urls_of_questions


def download_from_pcho():
    print('Попытка скачать с сайта https://polechudes-otvet.ru/')
    try:
        from bs4 import BeautifulSoup as bs
    except Exception as e:
        print('Ошибка импорта пакета bs4, "pip install bs4" please', e)
        return False
    faq = {}
    # pages = ('li', class_='previous').<a href>
    urls = get_urls_from_pcho()
    index = 0
    faq = {}
    print(f'Найдено {len(urls)} ссылок на задачи, попробуем сохранить')
    for url in urls:
        print(f'Сохраняем {index} из {len(urls)}')
        resp = requests.get(url)
        print(f'Сайт вернул код {resp.status_code}')
        if resp.status_code != 200:
            continue
        soup = bs(resp.text, 'html.parser')
        q = soup.find('em')
        a = soup.find('strong')
        if q and a:
            faq[index] = [q.text, a.text]
            index += 1

    return faq


def load_from_base():
    with open(base_file, 'r') as fl:
        faq = json.load(fl)
    return faq


def save_to_base(faq):
    with open(base_file, 'w') as fl:
        resp = json.dump(faq, fl)
    return resp


def main():
    global scores
    if os.path.isfile(base_file):
        faq = load_from_base()
    else:
        print('База вопросов и ответов не найдена, попробую скачать')
        # faq = random.choice([download_from_imho24(), download_from_pcho()])
        faq = download_from_imho24()
        save_to_base(faq)
        faq = load_from_base()

    qa_list = faq[random.choice(list(faq.keys()))]
    word = qa_list[1].split(':')[1].strip(' ').upper()
    question = qa_list[0].split(':')[1].strip(' ')
    out = ['_']*len(word)
    alphes = []
    players = [ x for x in scores.keys() ]
    index = 0
   # print(f'Вопрос: {question}')
    while ''.join(out) != word:
        w = False
        sector = random.choice(sectors)

        if index+1 > len(players):
            index = 0
        os.system('clear')
        print(f'Играет {players[index].capitalize()} ({scores[players[index]]}) ')
        if sector == 'propusk':
            print('Пропуск хода на барабане')
            time.sleep(2)
            index += 1
            continue
        elif sector[0] == 'x':
            print('На барабане удвоение очков, все выши очки удваиваются, если вы назовете вернуб букву')
        elif sector == 'open':
            print('Сектор позволяющий открыть любую букву на барабане')
            i = input('Введите порядковый номер буквы которую желаете открыть:\n')
            if int(i) > len(word):
                w  = word[-1].upper()
            else:
                w = word[int(i)-1].upper()
        else:
            print(f'На барабане {sector} очков!')

        if len(alphes)>0:
            print(f'Названные буквы: {", ".join(alphes)}')
        print(f'Вопрос: {question}')
        print(
            f'{out}\nБУКВ В СЛОВЕ: {len(out)}\nБУКВ НУЖНО ОТГАДАТЬ: { sum([1 for i in out if i == "_"]) }')
        if not w:
            w = input('Введите букву или слово целиком> ').upper()
        if len(w) > 1:
            if w == word:
                print(f'Вы выиграли!!! Слово {word}')
                if sector[0] == 'x':
                    scores[players[index]] *= 2
                else:
                    scores[players[index]] += int(sector)
                break
            elif w in ['/QUIT', '/EXIT', '/ВЫЙТИ', '/ЗАКОНЧИТЬ']:
                print('Выход из игры')
                break
            else:
                print('Слово названо не верно!')
                index += 1
                continue
        if len(w) < 1:
            continue

        if w.upper() in alphes:
            print('Такая буква уже была')
            time.sleep(2)
            continue


        alphes.append(w)
        if w not in word:
            print("Нет такой буквы! ")
            index += 1
            continue

        if sector[0] =='x':
            scores[players[index]] *= 2
        elif sector.isdigit():
            scores[players[index]] += int(sector)

        indexes = [i for i in range(len(word)) if word[i] == w]
        for i in indexes:
            out[i] = w
    print(f'Ответ: {word}')
    return ""


def add_users():
    global scores
    for _ in range(4):
        user = input('Введите имя игрока: ')
        if user.lower() in ['все','конец','exit','']:
            break
        scores[user] = 0





if __name__ == '__main__':
    args = [-1]

    add_users()
    if len(sys.argv) > 1:
        args = sys.argv[1:]
        if args[0] in ['-d', '--download']:
            faq = download_from_pcho()
            print(faq)
            if not faq:
                sys.exit(1)
            print(save_to_base(faq))
        else:
            print('Неизвестные параметры')
            sys.exit(1)
    while input('Еще раунд? ') in ['да','д','yes']:
        main()
    print('Конец игры')
    input('Нажмите ENTER для выхода')
