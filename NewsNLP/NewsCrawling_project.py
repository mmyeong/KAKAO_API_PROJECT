import requests
from bs4 import BeautifulSoup
import bs4.element
import datetime

#BeautifulSoup
def get_soup_obj(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)Chrome/63.0.3239.132 Safari/537.36'}
    res = requests.get(url,headers=headers)
    soup = BeautifulSoup(res.text,'lxml')

    return soup

#뉴스 정보
def get_top3_news_info(sec,sid):
    #Naver 아이콘
    default_img = "https://search.naver.com/search.naver?where=image&sm=tab_jum&query=naver#"

    #속보(경제)
    sec_url = "https://news.naver.com/main/list.nhn?mode=LSD&mid=sec"\
              +'&sid1='\
              + sid
    print('section url : ', sec_url)

    #상위 뉴스 HTML 가져오기
    soup = get_soup_obj(sec_url)

    #해당 분야 상위 뉴스 3개
    news_list3 =[]
    lis3 = soup.find('ul', class_='type06_headline').find_all('li',limit=3)

    for li in lis3:
        #title 뉴스제목 news_url : 뉴스 URL, image_url : 이미지 URL

        news_info = {
            "title": li.img.attrs.get('alt') if li.img else li.a.text.replace("\n", "").replace("\t", "").replace("\r",                                                                                                      ""),
            "date": li.find(class_="date").text,
            "news_url": li.a.attrs.get('href'),
            "image_url": li.img.attrs.get('src') if li.img else default_img
        }
        news_list3.append(news_info)

    return news_list3

#뉴스 본문
def get_news_contents(url):
    soup = get_soup_obj(url)
    body = soup.find('div',class_='_article_body_contents')

    news_contents = ''
    for content in body:
        if type(content) is bs4.element.NavigableString and len(content)>50:
            # content.strip() : whitepace 제거
            # 뉴스 요약을 위하여 '.' 마침표 뒤에 한칸을 띄워 문장을 구분하도록 함
            news_contents +=content.strip()+ ' '

    return news_contents

def get_naver_news_top3():
    #뉴스 결과 담기
    news_dic = dict()

    #sections = '경제'
    sections=['Eco']
    sections_ids = ['101']

    for sec,sid in zip(sections,sections_ids):
        news_info = get_top3_news_info(sec,sid)

        for news in news_info:
            #뉴스 본문
            news_url = news['news_url']
            news_contents = get_news_contents(news_url)

            #뉴스 정보 저장
            news['news_contents'] = news_contents

        news_dic[sec] = news_info

    return news_dic

#호출 상위 3개 뉴스 크롤링
news_dic = get_naver_news_top3()
#첫번째 결과
# print(news_dic['Eco'][0])

#뉴스 요약
from gensim.summarization.summarizer import summarize

#section 지정
my_section = 'Eco'
news_list3 = news_dic[my_section]
#뉴스 요약
for news_info in news_list3:
    #뉴스 본문이 10 문장 이하일 경우 결과 반환 x
    #요약하지 않고 본문에서 앞 3문장 사용
    try:
        snews_contents = summarize(news_info['news_contents'],word_count=20)
    except:
        snews_contents = None

    if not snews_contents:
        news_sentences = news_info['news_contents'].split('.')

        if len(news_sentences) > 3:
            snews_contents = '.'.join(news_sentences[:3])
        else:
            snews_contents = '.'.join(news_sentences)

    news_info['snews_contents'] = snews_contents

#요약 결과 - 첫번째 뉴스
print('***** 첫번째 뉴스 원문 *****')
print(news_list3[0]['news_contents'])
print('\n***** 첫번째 뉴스 요약문 *****')
print(news_list3[0]['snews_contents'])

#요약 결과 - 두번째 뉴스
print('***** 두번째 뉴스 원문 *****')
print(news_list3[1]['news_contents'])
print('\n***** 두번째 뉴스 요약문 *****')
print(news_list3[1]['snews_contents'])

import json
import NewsNLP.kakao_utils

KAKAO_TOKEN_FILENAME = 'kakao_tokens.json'
KAKAO_APP_KEY = '85ebcb4e804e57268332118b870d5fa4'
NewsNLP.kakao_utils.update_tokens(KAKAO_APP_KEY,KAKAO_TOKEN_FILENAME)

#경제카테고리
sections_ko = {'Eco' : '경제'}
#네이버 뉴스 URL
navernews_url = 'https://news.naver.com/main/home.nhn'
#list에 들어갈 내용 만들기
contents = []

#list 템플릿 형식 만들기
template = {
    "object_type" : "list",
    "header_title" : sections_ko[my_section] + "상위 뉴스 빅3",
    "header_link" : {
        "web_url": navernews_url,
        "mobile_web_url" : navernews_url
    },
    "contents" : contents,
    "button_title" : "네이버 뉴스 바로가기"
}

#내용 만들기
#각 리스트에 들어갈 내용 만들기
for news_info in news_list3:
    content ={
        'title' : news_info.get('title'),
        'description' : '작성일 : '+news_info.get('date'),
        'image_url' : news_info.get('image_url'),
        'image_width' : 50, 'image_height' : 50,
        'link' : {
            'web_url':news_info.get('news_url'),
            'mobile_web_url':news_info.get('news_url')
        }
    }
    contents.append(content)
#카카오 메시지 전송
res = NewsNLP.kakao_utils.send_message(KAKAO_TOKEN_FILENAME,template)
if res.json().get('result_code')==0:
    print('뉴스를 성공적으로 보냈습니다.')
else:
    print('뉴스를 성공적으로 보내지 못했습니다. 오류메시지 : ',res.json())


#텍스트 템플릿
for idx, news_info in enumerate(news_list3):
    template = {
        'object_type' : 'text',
        'text' : '* 제목 : ' + news_info.get('title')+\
                '\n\n* 요약 : ' + news_info.get('snews_contents'),
        'link' : {
            'web_url' : news_info.get('news_url'),
            'mobile_web_url' : news_info.get('news_url')
        },
        'button_title': '자세히 보기'
    }
    # 카카오 메시지 전송
    res = NewsNLP.kakao_utils.send_message(KAKAO_TOKEN_FILENAME, template)
    if res.json().get('result_code') == 0:
        print('뉴스를 성공적으로 보냈습니다.')
    else:
        print('뉴스를 성공적으로 보내지 못했습니다. 오류메시지 : ', res.json())


