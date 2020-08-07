from pymongo import MongoClient
import configparser
import json
import re
from datetime import datetime,timezone
from time import sleep
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerChannel

# Reading Configs
config = configparser.ConfigParser()
config.read("config.ini")

# Setting configuration values
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']

api_hash = str(api_hash)

phone = config['Telegram']['phone']
username = config['Telegram']['username']
client = TelegramClient(username,api_id,api_hash)

def connectDB():
    db_client = MongoClient("mongodb://localhost") #mongodb 링크
    db = db_client["coin_at"] #사용 database 이름
    return db

def extractSymbol(w):
    flag = True
    for i in w:
        if(ord(i)>=97 and ord(i)<=122):
            flag = False
            break
    if(flag):
        return w
    else:
        return None

async def main(phone):
    db = connectDB()
    await client.start()
    if not await client.is_user_authorized():
        client.send_code_request(phone)
        try:
            await client.sign_in(phone, input('Enter the code: '))
        except SessionPasswordNeededError:
            await client.sign_in(password=input('Password: '))
    user_input_channel = "https://t.me/shrimp_notice"
    #input("enter entity(telegram URL or entity id):")
    if user_input_channel.isdigit():
        entity = PeerChannel(int(user_input_channel))
    else:
        entity = user_input_channel
    channel = await client.get_entity(entity)
    offset_id = 0
    limit = 5
   #all_messages = []
    while True:
        #print("Current Offset ID is:", offset_id, "; Total Messages:", total_messages)
        history = await client(GetHistoryRequest(
            peer=channel,
            offset_id=offset_id,
            offset_date=None,
            add_offset=0,
            limit=limit,
            max_id=0,
            min_id=0,
            hash=0
        ))
        messages = history.messages
        for message in messages:
            msg = message.to_dict()
            title,date = msg["message"].rstrip(),msg["date"]
            #print(title,date)
            if("바이낸스(Binance)" in title):
                if("Binance Will List" in title or "Lists" in title):
                    symbols = list(filter(extractSymbol,re.split("[,:;\- \s \]\[ ㄱ-ㅎ|ㅏ-ㅣ|가-힣(.*)$]",title)))
                    for symbol in symbols:
                        binance_notice = db.binancenotices.find_one({"coin":symbol})
                        if(binance_notice is None):
                            db.binance_notice.insert_one({"coin":symbol,"title":title})
                            now = datetime.now(timezone.utc)
                            diff = (now-date).seconds
                            if(diff<=60):
                                print(title)
            elif("업비트(Upbit)" in title):
                if("[거래] 원화" in title and "마켓" in title and "신규" in title):
                    symbols = list(filter(extractSymbol,re.split("[,:;\- \s \]\[ ㄱ-ㅎ|ㅏ-ㅣ|가-힣(.*)$]",title)))
                    for symbol in symbols:
                        upbit_notice = db.upbitnotices.find_one({"coin":symbol})
                        if(upbit_notice is None):
                            now = datetime.now(timezone.utc)
                            db.upbitnotices.insert_one({"coin":symbol,"title":title,"keyword":"[거래]","checked":True,"createdAt":now.strftime("%Y-%m-%S %H:%M:%S")})
                            print(title)
                elif("[이벤트]" in title and "원화마켓" in title and ("오픈" in title or "지원" in title or "상장" in title) 
                and "결과" not in title and "당첨" not in title and "안내" not in title and "완료" not in title and "종료" not in title):
                    symbols = list(filter(extractSymbol,re.split("[,:;\- \s \]\[ ㄱ-ㅎ|ㅏ-ㅣ|가-힣(.*)$]",title)))
                    for symbol in symbols:
                        upbit_notice = db.upbitnotices.find_one({"coin":symbol})
                        if(upbit_notice is None):
                            now = datetime.now(timezone.utc)
                            db.upbitnotices.insert_one({"coin":symbol,"title":title,"keyword":"[거래]","checked":True,"createdAt":now.strftime("%Y-%m-%S %H:%M:%S")})
                            print(title)

        sleep(2)

with client:
    client.loop.run_until_complete(main(phone))