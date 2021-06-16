import cv2
import tensorflow.keras
import numpy as np
import beepy
import NewsNLP.kakao_utils

#컴퓨터 내장 소리 출력
def beepsound():
    beepy.beep(sound=6)

#카카오톡 메시지로 '졸음 방지 영상 링크 전송'
def send_music_link():
    KAKAO_TOKEN_FILENAME = '..\\NewsNLP\\kakao_tokens.json'
    KAKAO_APP_KEY = '85ebcb4e804e57268332118b870d5fa4'
    tokens = NewsNLP.kakao_utils.update_tokens(KAKAO_APP_KEY, KAKAO_TOKEN_FILENAME)



    #텍스트 메시지 보내기
    #군대 기상 나팔
    template = {
        'object_type' : 'text',
        'text' : '20초 이상 졸았습니다. 졸지마세요!!!',
        'link' : {
            'web_url' : 'https://www.youtube.com/watch?v=-44f3UIacx4',
            'mobile_web_url' : 'https://www.youtube.com/watch?v=-44f3UIacx4'
        },
        'button_title' : '잠깨는 노래 듣기'
    }

    #카카오 메시지 전송
    res = NewsNLP.kakao_utils.send_message(KAKAO_TOKEN_FILENAME, template)
    if res.json().get('result_code') == 0:
        print('텍스트 메시지를 성공적으로 보냈습니다.')
    else:
        print('텍스트 메시지를 보내지 못했습니다. 오류메시지 : ', res.json())

#이미지 전처리
def preprocessing(frame):
    #사이즈 조정
    size = (224,224)
    frame_resized = cv2.resize(frame, size, interpolation=cv2.INTER_AREA)

    #이미지 정규화
    frame_normalized = (frame_resized.astype(np.float32) / 127.0) - 1

    #이미지 차원 재조정 - 예측을 위해 reshape
    frame_reshaped = frame_normalized.reshape((1,224,224,3))

    return frame_reshaped

#학습된 모델 불러오기
model_filename = 'keras_model.h5'
model = tensorflow.keras.models.load_model(model_filename)

#카메라
capture = cv2.VideoCapture(0)

#캡쳐 프레임 사이즈 조절
capture.set(cv2.CAP_PROP_FRAME_WIDTH,320)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT,240)

sleep_cnt = 1 #20초간 '졸음'상태 확인
while True:
    ret, frame = capture.read()
    if ret == True:
        print('성공')

    #이미지 뒤집기
    frame_fliped = cv2.flip(frame,1)

    #이미지 출력
    cv2.imshow('VideoFrame',frame_fliped)

    #1초마다 검사하며, 아무키나 누르면 종료
    if cv2.waitKey(200)>0:
        break

    #데이터 전처리
    preprocessed = preprocessing(frame_fliped)

    #예측
    prediction = model.predict(preprocessed)

    if prediction[0,0] < prediction[0,1]:
        print('졸림 상태')
        sleep_cnt += 1

        #졸린 상태가 20초 지속되면 소리와 카카오톡
        if sleep_cnt%20 ==0:
            sleep_cnt = 1
            print('20초간 졸고 있네요 !!!')
            beepsound()
            send_music_link()
            break##1번만 알람이 오면 프로그램 정지 반복 원한다면 주석으로막기
    else:
        print('깨어는 상태')
        sleep_cnt=1

# 카메라 객체 반환
capture.release()
# 화면에 나타난 윈도우들을 종료
cv2.destroyAllWindows()
