# Telegram 코인 공지방 그룹 메시지 Crawling

- python, telethon 활용

## 설정

- api_id 와 an api_hash는 https://my.telegram.org/ 의 API development tools 에서 발급 받으시면 됩니다.

```
root에 config.ini 파일 생성, 아래와 같이 입력

[Telegram]
# no need for quotes
api_id = ""
api_hash = ""
phone = ""     //telegram에서 사용하는 번호
username = ""  //telegram 계정 username

```

## 패키지 설치

```
pip3 install -r requirements.txt
```

## 실행

```
python3 run.py
```
