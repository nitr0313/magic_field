import requests
import random
import json
import sys

base_file = 'base_q.json'


def download_q():
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
    while True:
        resp = requests.get(url)
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
    return all_urls_of_questions


def download_b():
    try:
        from bs4 import BeautifulSoup as bs
    except Exception as e:
        print('Ошибка импорта пакета bs4, "pip install bs4" please', e)
        return False
    # pages = ('li', class_='previous').<a href>
    urls = get_urls_from_pcho()
    for url in urls:
        resp = requests.get(url)
        soup = bs(resp.text, 'html.parser')
        # soup.findAll()
    pass

    # <a href = "https://polechudes-otvet.ru/ustanovit-igru/" > Установить игру < /a >


def load_from_base():
    with open(base_file, 'r') as fl:
        faq = json.load(fl)
    return faq


def save_to_base(faq):
    with open(base_file, 'w') as fl:
        resp = json.dump(faq, fl)
    return resp


def main():
    try:
        faq = load_from_base()
    except Exception as e:
        print('База вопросов и ответов не найдена, попробую скачать', e)
        faq = download_q()
        save_to_base(faq)
        faq = load_from_base()
    qa_list = faq[random.choice(list(faq.keys()))]
    word = qa_list[1].split(':')[1].strip(' ').upper()
    question = qa_list[0].split(':')[1].strip(' ')
    out = ['_']*len(word)
    alphes = []
    print(f'Вопрос: {question}')
    while ''.join(out) != word:
        print(
            f'CЛОВО: {out}\nБУКВ В СЛОВЕ: {len(out)}\nБУКВ НУЖНО ОТГАДАТЬ: {sum([1 for i in out if i == "_"])}')
        w = input('Введите букву или слово целиком> ').upper()
        if len(w) > 1:
            if w == word:
                print(f'Вы выиграли!!! Слово {word}')
                break
            elif w in ['/QUIT', '/EXIT', '/ВЫЙТИ', '/ЗАКОНЧИТЬ']:
                print('Выход из игры')
                break
            elif w in ['/ВОПРОС', '/ПОВТОРИТЬ', '/HELP']:
                print(f'Вопрос: {question}')
                continue
            else:
                print('Слово названо не верно!')
                continue
        if w not in word:
            print("Нет такой буквы! ")
            continue
        elif w in alphes:
            print("Буква уже называлась!")
            continue
        alphes.append(w)
        indexes = [i for i in range(len(word)) if word[i] == w]
        for i in indexes:
            out[i] = w
    print(f'Ответ: {word}')
    return ""


if __name__ == '__main__':
    args = [-1]
    if len(sys.argv) > 1:
        args = sys.argv[1:]
        if args[0] in ['-d', '--download']:
            faq = download_b()
            print(faq)
            if not faq:
                sys.exit(1)
            print(save_to_base(faq))
        else:
            print('Неизвестные параметры')
            sys.exit(1)
    main()
    print('Конец игры')
    input('Нажмите ENTER для выхода')
