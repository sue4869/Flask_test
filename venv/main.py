#먼저 static과 templates라는 Directory를 만들어야 한다
#flask : 서버를 구축할 수 있도록 도와주는 프레임워크
#실행하는 순간 내 PC가 서버(html코드 같은 것 서비스한다)의 역활을 한다.

from flask import Flask, make_response, jsonify, request, render_template

app = Flask(__name__)


from konlpy.tag import Okt
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model
import json
import os

#감정 분석
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

okt = Okt() #한국의 형태소분석 --> 각 형태소마다 token화 한다.
tokenizer = Tokenizer(19417, oov_token = 'OOV')
with open('wordIndex.json') as json_file:
  word_index = json.load(json_file)
  tokenizer.word_index = word_index

loaded_model = load_model('best_model.h5')
def sentiment_predict(new_sentence):
    print(new_sentence)
    max_len = 30
    stopwords = ['의','가','이','은','들','는','좀','잘','걍','과','도','를','으로','자','에','와','한','하다']
    new_sentence = okt.morphs(new_sentence, stem=True) # 토큰화
    new_sentence = [word for word in new_sentence if not word in stopwords] # 불용어 제거
    encoded = tokenizer.texts_to_sequences([new_sentence]) # 정수 인코딩
    pad_new = pad_sequences(encoded, maxlen = max_len) # 패딩
    score = float(loaded_model.predict(pad_new)) # 예측
    if score >= 0.5:
        print("{:.2f}% 확률로 긍정 리뷰입니다.".format(score*100)) #:.2f --> 소숫점 2자리 수까지만 표현
    else:
        print("{:.2f}% 확률로 부정 리뷰입니다.".format((1-score)*100))


    #---------추가----------
    if 0.8 <= score <1:
        return "매우긍정"
    elif 0.6 <= score < 0.8:
        return "긍정"
    elif 0.4 <= score <= 0.6:
        return "중립"
    elif 0.2 <= score < 0.4:
        return "부정"
    else:
        return "매우부정"
    #-----------------------

#네이버 영화 리뷰 크롤링
from bs4 import BeautifulSoup
import urllib.request as req

page_num = 1
emotion_result = {"매우긍정":0 ,"긍정":0, "중립":0,"부정":0,"매우부정":0}
while True:
    code = req.urlopen("https://movie.naver.com/movie/bi/mi/pointWriteFormList.nhn?code=189069&type=after&isActualPointWriteExecute=false&isMileageSubscriptionAlready=false&isMileageSubscriptionReject=false&page={}".format(page_num))
    soup = BeautifulSoup(code, "html.parser")
    comment = soup.select("li > div.score_reple > p > span")
    if len(comment) == 0:
        break
    for i in comment:
        i = i.text.strip()
        if i == "관람객":
            continue

        result = sentiment_predict(i)
        emotion_result[result] += 1
        print("--------------------------------")
    page_num += 1
    if page_num == 2:
        break

review_num_total = sum(emotion_result.values())
emotion_percent1 = (emotion_result["매우긍정"]/review_num_total)*100
emotion_percent2 = (emotion_result["긍정"]/review_num_total)*100
emotion_percent3 = (emotion_result["중립"]/review_num_total)*100
emotion_percent4 = (emotion_result["부정"]/review_num_total)*100
emotion_percent5 = (emotion_result["매우부정"]/review_num_total)*100

#----------------------------달라지는 곳
#pyecharts bar3d검색 >> BD예제 코드 복사

from pyecharts import Bar3D

bar3d = Bar3D("", width=700, height=500)
x_axis = ["매우긍정", "긍정", "중립", "부정", "매우부정"]
y_aixs = []
data = [[0,0,emotion_result["매우긍정"]],[0,1,emotion_result["긍정"]],[0,2,emotion_result["중립"]],[0,3,emotion_result["부정"]],[0,4,emotion_result["매우부정"]]]
range_color = ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf',
               '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
bar3d.add("", x_axis, y_aixs, [[d[1], d[0], d[2]] for d in data], is_visualmap=True,
          visual_range=[0, 20], visual_range_color=range_color, grid3d_width=200, grid3d_depth=40)
bar3d.show_config()
bar3d.render("./bar3d.html")

from pyecharts import Pie

attr = ["매우긍정", "긍정", "중립", "부정", "매우부정"]
v1 = [emotion_result["매우긍정"], emotion_result["긍정"], emotion_result["중립"], emotion_result["부정"], emotion_result["매우부정"]]
pie = Pie("")

pie.add("", attr, v1, is_label_show=True)
pie.show_config()
pie.render("./pie.html")

with open("./bar3d.html","r",encoding='UTF8') as f:
    bar_html = f.read()

with open("./pie.html","r",encoding='UTF8') as f:
     pie_html = f.read()



@app.route('/')
def main():
    return render_template("index.html",emotion1="매우 긍정 {} % :".format(emotion_percent1),
                           emotion2="긍정 {} % :".format(emotion_percent2),
                           emotion3="부정 {} % :".format(emotion_percent3),
                           emotion4="매우 부정 {} % :".format(emotion_percent4),
                           bar3d=bar_html, pie=pie_html)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)

