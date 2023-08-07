import streamlit as st
import time
import requests
import json
from datetime import timedelta
import pandas as pd

def get_openai_request(messages, deployment_name, **kwargs):
    url = "https://oai-internal.openai.azure.com/openai/deployments/%s/chat/completions?api-version=2023-03-15-preview"
    print("Prompt....")
    print(messages)
    r = requests.post(url % deployment_name,
      json = {
        'messages': messages,
        **kwargs
      },
      headers={'api-key': '216b7e617e034a28adb5dbe86044b082', 'Content-Type': 'application/json'}
    )
    return r

def gen_chat(prompt, **kwargs):
    messages = [
        {
            "role": "system",
            "content": "You are AI who analyst agent satisfaction evaluator."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
#   try:
    r = get_openai_request(messages, 'gpt-4', **kwargs) # davinci-003, turbo-trial, gpt-4
    j = r.json()
    if 'error' in j:
      return {
       'choices': [ {'message': {'content': None}, 'finish_reason': j['error']['message']}],
       'usage': {
          'completion_tokens': 0,
          'prompt_tokens': 0
       }
    }
    else:
      return j
#   except Exception as e:
#     return
#     {
#        'choices': [ {'message': {'content': None}, 'finish_reason': e.__class__.__name__ + ': ' + str(e)}],
#        'usage': {
#           'completion_tokens': 0,
#           'prompt_tokens': 0
#        }
#     }

st.set_page_config(page_title="Appman - Contact Center Analyzer", page_icon=":shark:")
st.markdown(
    """
        <style>
            textarea {
                font-size: 1.125rem !important;
            }
            p {
                font-size: 1.25rem !important;
            }
        </style>
    """,
    unsafe_allow_html=True,
)

st.title(":red[App]Man - Contact Center Analyzer")

audio_file = st.file_uploader(
    label="Upload an audio file",
    type=["wav", "m4a", "mp3"], 
    accept_multiple_files=False,
)

if audio_file is not None:
    name = audio_file.name
    value: str = ""
    score: int = 0
    secs: float = 3

    

    if 'transcribed' not in st.session_state:
        with st.spinner('Recognizing...'):
            time.sleep(secs)
        st.success('Done!')
        st.session_state['transcribed'] = 'done'

    message_completed = "{ \"sound\": \"https://mp3buckets.s3.eu-central-1.amazonaws.com/75c13f471963eb8108eca5ed25a4ecfcc385decabc2e2e98de1f394854db68cc06bd844570bbd40cd796d9eb4e8dc3f00f95b92fab84b72a0dcf2097f1824aed.mp3\", \"content\": [ { \"StartTime\": 310, \"EndTime\": 4220, \"VoiceStart\": 310, \"VoiceEnd\": 4220, \"Speaker\": \"SPK_1\", \"text\": \"สวัสดีค่ะเรียนสายอยู่กับคุณพิมพ์ชนก ใจดีใช่มั้ยค่ะ\" }, { \"StartTime\": 4670, \"EndTime\": 6140, \"VoiceStart\": 4670, \"VoiceEnd\": 6140, \"Speaker\": \"SPK_2\", \"text\": \"ค่ะ ติดต่อจากไหนคะ\" }, { \"StartTime\": 6350, \"EndTime\": 17820, \"VoiceStart\": 6350, \"VoiceEnd\": 17820, \"Speaker\": \"SPK_1\", \"text\": \"ดิฉันนางสาวกนกพร ร่ำรวย ตัวแทนจากบริษัทแอพแมนประกันภัยจำกัดตัวแทนเลขที่ 1234567890 ค่ะสะดวกเรียนสายสักคู่ไหมค่ะ\" }, { \"StartTime\": 18150, \"EndTime\": 19190, \"VoiceStart\": 18150, \"VoiceEnd\": 19190, \"Speaker\": \"SPK_2\", \"text\": \"ได้ค่ะ\" }, { \"StartTime\": 19260, \"EndTime\": 25940, \"VoiceStart\": 19260, \"VoiceEnd\": 25940, \"Speaker\": \"SPK_1\", \"text\": \"โอเคคะขอประทานโทษนะคะปกติคุณพิมพ์ชนกเดินทางด้วยรถส่วนตัวหรือเป็นรถสาธารณะค่ะ\" }, { \"StartTime\": 26450, \"EndTime\": 27580, \"VoiceStart\": 26450, \"VoiceEnd\": 27580, \"Speaker\": \"SPK_2\", \"text\": \"รถส่วนตัวค่ะ\" }, { \"StartTime\": 27850, \"EndTime\": 32130, \"VoiceStart\": 27850, \"VoiceEnd\": 32130, \"Speaker\": \"SPK_1\", \"text\": \"ดีเลยค่ะตอนนี้ทางเราอ่ะค่ะมีประกันอุบัติเหตุมานำเสนอค่ะ\" }, { \"StartTime\": 32250, \"EndTime\": 65630, \"VoiceStart\": 32250, \"VoiceEnd\": 65630, \"Speaker\": \"SPK_1\", \"text\": \"ซึ่งจะคุ้มครองเมื่อเสียชีวิตหรือพิการจากอุบัติเหตุฆาตกรรมลอบทำร้ายขับขี่โดยสารรถจักรยานยนต์และจากการก่อการร้ายตัวนี้ค่ะครอบคลุมถึงอุบัติเหตุที่เกิดจากยานยนต์สาธารณะและยานยนต์ส่วนตัวเงินช่วยเหลือค่าปลงศพเนี่ยค่ะกรณีเสียชีวิตจากอุบัติเหตุและค่ารักษาพยาบาลไม่จำกัดจำนวนครั้งอุบัติเหตุโดยค่ารักษาต่ออุบัติเหตุไม่เกินทุนที่กำหนดสูงสุดอยู่ที่ 100,000 บาทจ่ายเพิ่มอีก หนึ่ง เท่าจากอุบัติเหตุที่เกิดในวันหยุดราชการรวมวันเสาร์อาทิตย์\" }, { \"StartTime\": 65760, \"EndTime\": 73760, \"VoiceStart\": 65760, \"VoiceEnd\": 73760, \"Speaker\": \"SPK_1\", \"text\": \"หรือจ่ายเพิ่มอีก หนึ่งเท่าจากอุบัติเหตุขณะโดยสารยานพาหนะสาธารณะ คุณพิมพ์ชนก มีความคิดเห็นว่าอย่างไรบ้างคะ\" }, { \"StartTime\": 74830, \"EndTime\": 76390, \"VoiceStart\": 74830, \"VoiceEnd\": 76390, \"Speaker\": \"SPK_2\", \"text\": \"น่าสนใจนะคะ\" }, { \"StartTime\": 77010, \"EndTime\": 81140, \"VoiceStart\": 77010, \"VoiceEnd\": 81140, \"Speaker\": \"SPK_1\", \"text\": \"โอเคค่ะขอโทษนะคะไม่ทราบว่าตอนนี้คุณพิมพ์ชนกอายุเท่าไหร่หรอคะ\" }, { \"StartTime\": 81400, \"EndTime\": 82780, \"VoiceStart\": 81400, \"VoiceEnd\": 82780, \"Speaker\": \"SPK_2\", \"text\": \"อายุ 25 ค่ะ\" }, { \"StartTime\": 82820, \"EndTime\": 93220, \"VoiceStart\": 82820, \"VoiceEnd\": 93220, \"Speaker\": \"SPK_1\", \"text\": \"อ้ออายุ 25 ดีเลยค่ะตอนนี้ค่าเบี้ยประกันนะคะจะอยู่ที่ 3,000 บาทตกอยู่ที่เดือนละ 250 บาทหรือวันละ 9 บาทเท่านั้นเองค่ะคุณพิมพ์ชนกสนใจไหมคะ\" }, { \"StartTime\": 93950, \"EndTime\": 95830, \"VoiceStart\": 93950, \"VoiceEnd\": 95830, \"Speaker\": \"SPK_2\", \"text\": \"ถ้าจะสมัครอะคะ\" }, { \"StartTime\": 96700, \"EndTime\": 98970, \"VoiceStart\": 96700, \"VoiceEnd\": 98970, \"Speaker\": \"SPK_2\", \"text\": \"ต้องดำเนินการยังไงบ้างคะ\" }, { \"StartTime\": 99010, \"EndTime\": 103980, \"VoiceStart\": 99010, \"VoiceEnd\": 103980, \"Speaker\": \"SPK_1\", \"text\": \"คุณพิมพ์ชนกสะดวกชำระค่าเบี้ยทั้งหมดหรือว่าสะดวกเป็นแบ่งชำระรายเดือนค่ะ\" }, { \"StartTime\": 104740, \"EndTime\": 105790, \"VoiceStart\": 104740, \"VoiceEnd\": 105790, \"Speaker\": \"SPK_2\", \"text\": \"แบ่งชำระรายเดือน\" }, { \"StartTime\": 105800, \"EndTime\": 109550, \"VoiceStart\": 105800, \"VoiceEnd\": 109550, \"Speaker\": \"SPK_1\", \"text\": \"ค่ะโอเคค่ะจะเป็นการตัดบัตรเครดิตหรือว่าเป็นเงินสดค่ะ\" }, { \"StartTime\": 110250, \"EndTime\": 111160, \"VoiceStart\": 110250, \"VoiceEnd\": 111160, \"Speaker\": \"SPK_2\", \"text\": \"เงินสดคะ\" }, { \"StartTime\": 111200, \"EndTime\": 118080, \"VoiceStart\": 111200, \"VoiceEnd\": 118080, \"Speaker\": \"SPK_1\", \"text\": \"โอเคได้เลยค่ะเดี๋ยวทางเราอ่ะค่ะจะส่งเป็นคิวอาร์โค้ดให้กับทางคุณพิมพ์ชนกหลังจากจบการสนทนานะคะ\" }, { \"StartTime\": 118370, \"EndTime\": 119120, \"VoiceStart\": 118370, \"VoiceEnd\": 119120, \"Speaker\": \"SPK_2\", \"text\": \"ได้ค่ะ\" }, { \"StartTime\": 119310, \"EndTime\": 142260, \"VoiceStart\": 119310, \"VoiceEnd\": 142260, \"Speaker\": \"SPK_1\", \"text\": \"โอเคค่ะต่อไปจะเป็นโพลใน 4 ของทางบริษัทนะคะขออนุญาตให้ข้อมูลเพิ่มเติมค่ะกระบวนการจะมีการยินยอมทั้งหมด สอง ส่วน หนึ่ง คือยินยอมให้ทางบริษัทเก็บรวบรวมใช้และเปิดเผยข้อมูลส่วนบุคคล สอง ยินยอมให้ใช้ข้อมูลเพื่อการตลาดทางตรงและการส่งเสริมการขายค หนึ่ง รบกวนคุณพิมพ์ชนกตอบยินยอมนะคะ\" }, { \"StartTime\": 142360, \"EndTime\": 145950, \"VoiceStart\": 142360, \"VoiceEnd\": 145950, \"Speaker\": \"SPK_1\", \"text\": \"ส่วนข้อที่ สอง 3 ารถตอบยินยอมหรือไม่ยินยอมก็ได้ค่ะ\" }, { \"StartTime\": 147010, \"EndTime\": 147740, \"VoiceStart\": 147010, \"VoiceEnd\": 147740, \"Speaker\": \"SPK_2\", \"text\": \"ได้ค่ะ\" }, { \"StartTime\": 148470, \"EndTime\": 178480, \"VoiceStart\": 148470, \"VoiceEnd\": 178480, \"Speaker\": \"SPK_1\", \"text\": \"ข้าพเจ้ายินยอมให้บริษัทเก็บรวบรวมและใช้ข้อมูลส่วนบุคคลได้แก่ชื่อนามสกุลหมายเลขโทรศัพท์อีเมลที่อยู่เป็นต้นและข้อมูลอ่อนไหวตามที่พระราชบัญญัติคุ้มครองข้อมูลส่วนบุคคลพุทธศักราช 2,562 กำหนดข้าพเจ้าเจ้าของข้อมูลส่วนบุคคลสามารถถอนความยินยอมได้ทุกเมื่อแต่การถอนความยินยอมจะไม่กระทบซึ่งสิทธิของบริษัทในการรวบรวมใช้เปิดเผยข้อมูลส่วนบุคคลใดๆ\" }, { \"StartTime\": 178600, \"EndTime\": 186950, \"VoiceStart\": 178600, \"VoiceEnd\": 186950, \"Speaker\": \"SPK_1\", \"text\": \"ตามฐานข้อมูลทางกฎหมายอื่นภายใต้พระราชบัญญัติคุ้มครองข้อมูลส่วนบุคคลพุทธศักราช 2,562 ยินยอมหรือไม่คะ\" }, { \"StartTime\": 187260, \"EndTime\": 188080, \"VoiceStart\": 187260, \"VoiceEnd\": 188080, \"Speaker\": \"SPK_2\", \"text\": \"ยินยอมค่ะ\" }, { \"StartTime\": 188890, \"EndTime\": 196580, \"VoiceStart\": 188890, \"VoiceEnd\": 196580, \"Speaker\": \"SPK_1\", \"text\": \"ขั้นตอนต่อไปจะเป็นการยืนยันการซื้อประกันภัยนะคะรบกวนคุณพิมพ์ชนกตอบว่าตกลงซื้อประกันภัยให้หน่อยนะคะ\" }, { \"StartTime\": 197030, \"EndTime\": 197550, \"VoiceStart\": 197030, \"VoiceEnd\": 197550, \"Speaker\": \"SPK_2\", \"text\": \"ได้คะ\" }, { \"StartTime\": 200100, \"EndTime\": 213490, \"VoiceStart\": 200100, \"VoiceEnd\": 213490, \"Speaker\": \"SPK_1\", \"text\": \"คุณพิมพ์ชนกใจดีมีความประสงค์ที่จะซื้อประกันภัยอุบัติเหตุกับบริษัทแอ๊บแมนประกันภัยจำกัดโดยความคุ้มครองจะเป็นไปตามรายละเอียดข้างต้นที่ได้กล่าวไว้คุณพิมพ์ชนกตกลงที่จะทำประกันภัยหรือไม่ค่ะ\" }, { \"StartTime\": 214510, \"EndTime\": 215640, \"VoiceStart\": 214510, \"VoiceEnd\": 215640, \"Speaker\": \"SPK_2\", \"text\": \"ตกลงทำประกันค่ะ\" }, { \"StartTime\": 216340, \"EndTime\": 246710, \"VoiceStart\": 216340, \"VoiceEnd\": 246710, \"Speaker\": \"SPK_1\", \"text\": \"ขอบคุณค่ะสำหรับเล่มกรมธรรม์จะส่งตามไปให้ไม่เกิน 7 วันทำการนะคะและถ้าหากคุณพิมพ์ชนกอยากได้รายละเอียดความคุ้มครองเพิ่มเติมสามารถติดต่อดิฉันได้เลยนะคะหรือสามารถอ่านตามเล่มกรมธรรม์ที่จะจัดส่งไปที่บ้านได้เลยค่ะและหากอ่านเรียบร้อยแล้วไม่ตรงกับที่ทางเราแจ้งไว้สามารถบอกยกเลิกได้ภายใน 30 วันหลังจากได้รับกรมธรรม์นะคะขอบคุณคุณพิมพ์ชนกสำหรับการไว้วางใจในการซื้อประกันภัยกับบริษัทแอ๊บแมนประกันภัยจำกัดค่ะ\" }, { \"StartTime\": 247010, \"EndTime\": 250380, \"VoiceStart\": 247010, \"VoiceEnd\": 250380, \"Speaker\": \"SPK_1\", \"text\": \"ขออนุญาตวางสายนะคะขอบคุณค่ะขอบคุณค่ะ\" } ], \"service\": \"Standard\", \"status\": \"Completed\", \"language\": \"th-TH\", \"filename\": \"Telesale-completed\", \"date\": \"1691056920281\" }"
    message_no_license = "{ \"sound\": \"https://mp3buckets.s3.eu-central-1.amazonaws.com/900e25ac0b0dd9fdfd6e0d0a94c39082d6b1104a09a27fa749cc11fd5767fa048038073a271b08c21ff498b14c1f88e8c8baaf6caabcbc61a36012996aaa39d5.mp3\", \"content\": [ { \"StartTime\": 1000, \"EndTime\": 4490, \"VoiceStart\": 1000, \"VoiceEnd\": 4490, \"Speaker\": \"SPK_1\", \"text\": \"สวัสดีค่ะเรียนสายอยู่กับคุณพิมพ์ชนก ใจดีใช่มั้ยขา\" }, { \"StartTime\": 4560, \"EndTime\": 6230, \"VoiceStart\": 4560, \"VoiceEnd\": 6230, \"Speaker\": \"SPK_2\", \"text\": \"ใช่ค่ะติดต่อจากไหนคะ\" }, { \"StartTime\": 6290, \"EndTime\": 12570, \"VoiceStart\": 6290, \"VoiceEnd\": 12570, \"Speaker\": \"SPK_1\", \"text\": \"ดิฉันนางสาวกนกพร ร่ำรวยนะคะตัวแทนจากบริษัทแอพแมนประกันภัยจำกัดค่ะสะดวกเป็นสายสักคู่\" }, { \"StartTime\": 12580, \"EndTime\": 14510, \"VoiceStart\": 12580, \"VoiceEnd\": 14510, \"Speaker\": \"SPK_2\", \"text\": \"ไหมค่ะได้ค่ะ\" }, { \"StartTime\": 14720, \"EndTime\": 20890, \"VoiceStart\": 14720, \"VoiceEnd\": 20890, \"Speaker\": \"SPK_1\", \"text\": \"ขอประทานโทษนะคะปกติคุณพิมพ์ชนกอ่ะค่ะเดินทางด้วยรถส่วนตัวหรือรถสาธารณะค่ะ\" }, { \"StartTime\": 21340, \"EndTime\": 23070, \"VoiceStart\": 21340, \"VoiceEnd\": 23070, \"Speaker\": \"SPK_2\", \"text\": \"เป็นรถยนต์ส่วนตัวค่ะ\" }, { \"StartTime\": 23150, \"EndTime\": 31530, \"VoiceStart\": 23150, \"VoiceEnd\": 31530, \"Speaker\": \"SPK_1\", \"text\": \"ดีเลยค่ะตอนนี้ทางเรานะคะมีประกันอุบัติเหตุมานำเสนอค่ะซึ่งจะคุ้มครองเมื่อเสียชีวิตหรือพิการจากอุบัติเหตุฆาตกรรมรอบทำร้าย\" }, { \"StartTime\": 31720, \"EndTime\": 50010, \"VoiceStart\": 31720, \"VoiceEnd\": 50010, \"Speaker\": \"SPK_1\", \"text\": \"ขับขี่โดยสารรถจักรยานยนต์และจากการก่อการร้ายค่ะตัวนี้อะค่ะครอบคลุมถึงอุบัติเหตุที่เกิดจากยานยนต์สาธารณะและยานยนต์ส่วนตัวค่ะซึ่งเงินช่วยเหลือค่าปลงศพค่ะกรณีเสียชีวิตจากอุบัติเหตุและค่ารักษาพยาบาลไม่จำกัดจำนวนครั้งอุบัติเหตุโดยค่ารักษา\" }, { \"StartTime\": 50750, \"EndTime\": 66740, \"VoiceStart\": 50750, \"VoiceEnd\": 66740, \"Speaker\": \"SPK_1\", \"text\": \"ต่ออุบัติเหตุค่ะไม่เกินทุนที่กำหนดสูงสุด 100,000 บาทจ่ายเพิ่มอีก หนึ่ง เท่าจากอุบัติเหตุที่เกิดในวันหยุดราชการรวมถึงวันเสาร์อาทิตย์หรือจ่ายเพิ่มอีก หนึ่ง เท่าจากอุบัติเหตุขณะโดยสารยานยนต์สาธารณะคุณพิมพ์ชนกมีความคิดเห็นอย่างไรบ้างคะ\" }, { \"StartTime\": 67130, \"EndTime\": 68920, \"VoiceStart\": 67130, \"VoiceEnd\": 68920, \"Speaker\": \"SPK_2\", \"text\": \"เออน่าสนใจดีนะค่ะ\" }, { \"StartTime\": 69050, \"EndTime\": 72960, \"VoiceStart\": 69050, \"VoiceEnd\": 72960, \"Speaker\": \"SPK_1\", \"text\": \"เอ่อขอโทษนะคะไม่ทราบว่าตอนนี้อ่ะคะคุณพิมพ์ชนกอายุเท่าไหร่คะ\" }, { \"StartTime\": 73010, \"EndTime\": 74080, \"VoiceStart\": 73010, \"VoiceEnd\": 74080, \"Speaker\": \"SPK_2\", \"text\": \"25 ค่ะ\" }, { \"StartTime\": 74170, \"EndTime\": 82230, \"VoiceStart\": 74170, \"VoiceEnd\": 82230, \"Speaker\": \"SPK_1\", \"text\": \"อายุ 25 ใช่ไหมคะตอนนี้ค่าเบี้ยประกันนะคะจะอยู่ที่ 3,000 บาทนะคะตกเดือนละ 250 บาทคะหรือวันละ 9 บาทเท่านั้นเองค่ะ\" }, { \"StartTime\": 82340, \"EndTime\": 83880, \"VoiceStart\": 82340, \"VoiceEnd\": 83880, \"Speaker\": \"SPK_1\", \"text\": \"คุณพิมพ์ชนกสนใจไหมคะ\" }, { \"StartTime\": 84610, \"EndTime\": 88460, \"VoiceStart\": 84610, \"VoiceEnd\": 88460, \"Speaker\": \"SPK_2\", \"text\": \"อืมถ้าสนใจทำประกันนี้ต้องดำเนินการยังไงต่อบ้างคะ\" }, { \"StartTime\": 88630, \"EndTime\": 93480, \"VoiceStart\": 88630, \"VoiceEnd\": 93480, \"Speaker\": \"SPK_1\", \"text\": \"คุณพิมพ์ชนกสะดวกชำระค่าเบี้ยราคาจ่ายทั้งหมดหรือว่าชำระเป็นรายเดือนค่ะ\" }, { \"StartTime\": 93930, \"EndTime\": 95520, \"VoiceStart\": 93930, \"VoiceEnd\": 95520, \"Speaker\": \"SPK_2\", \"text\": \"เป็นแบบรายเดือนค่ะ\" }, { \"StartTime\": 95830, \"EndTime\": 98370, \"VoiceStart\": 95830, \"VoiceEnd\": 98370, \"Speaker\": \"SPK_1\", \"text\": \"เอ่อจะเป็นการตัดผ่านบัตรเครดิตหรือว่าเงินสดคะ\" }, { \"StartTime\": 98380, \"EndTime\": 100000, \"VoiceStart\": 98380, \"VoiceEnd\": 100000, \"Speaker\": \"SPK_2\", \"text\": \"เงินสดค่ะ\" }, { \"StartTime\": 100010, \"EndTime\": 105900, \"VoiceStart\": 100010, \"VoiceEnd\": 105900, \"Speaker\": \"SPK_1\", \"text\": \"ได้ค่ะเดี๋ยวทางเราจะทำการส่งคิวอาร์โค้ดให้กับทางคุณพิมพ์ชนกนะคะหลังจบการสนทนา\" }, { \"StartTime\": 105910, \"EndTime\": 107270, \"VoiceStart\": 105910, \"VoiceEnd\": 107270, \"Speaker\": \"SPK_2\", \"text\": \"ค่ะได้ค่ะ\" }, { \"StartTime\": 107310, \"EndTime\": 115840, \"VoiceStart\": 107310, \"VoiceEnd\": 115840, \"Speaker\": \"SPK_1\", \"text\": \"โอเคค่ะต่อไปจะเป็น policy ของทางบริษัทนะคะขออนุญาตให้ข้อมูลเพิ่มเติมค่ะกระบวนการจะมีการยินยอม สอง ส่วนด้วยกันนะคะโดยส่วนที่ หนึ่ง นะคะ\" }, { \"StartTime\": 116000, \"EndTime\": 134710, \"VoiceStart\": 116000, \"VoiceEnd\": 134710, \"Speaker\": \"SPK_1\", \"text\": \"จะยินยอมให้กับทางบริษัทเก็บรวบรวมใช้และเปิดเผยข้อมูลส่วนบุคคล สอง ยินยอมให้ใช้ข้อมูลเพื่อการตลาดทางตรงและการส่งเสริมการขายค่ะข้อที่ หนึ่ง นะคะรบกวนคุณพิมพ์ชนกนะคะตอบยินยอมนะคะแล้วก็ในส่วนของข้อที่ สอง สามารถตอบยินยอมหรือไม่ยินยอมก็ได้นะคะ\" }, { \"StartTime\": 134990, \"EndTime\": 135280, \"VoiceStart\": 134990, \"VoiceEnd\": 135280, \"Speaker\": \"SPK_2\", \"text\": \"ค่ะ\" }, { \"StartTime\": 136350, \"EndTime\": 159760, \"VoiceStart\": 136350, \"VoiceEnd\": 159760, \"Speaker\": \"SPK_1\", \"text\": \"ข้อที่ หนึ่ง ค่ะข้าพเจ้ายินยอมที่จะเปิดเผยข้อมูลสุขภาพและประวัติการรักษาพยาบาลของข้าพเจ้าทั้งหมดโดยสิ้นเชิงให้แก่บริษัทแอพแมนประกันภัยจำกัดตัวแทนประกันภัยของบริษัทหรือผู้แทนของบริษัทเพื่อทำการขอเอาประกันภัยการจ่ายเงินตามกรมธรรม์ประกันภัยหรือดำเนินการใดๆที่เกี่ยวข้องกับกรมธรรม์ประกันภัยยินยอมหรือไม่คะ\" }, { \"StartTime\": 159990, \"EndTime\": 160840, \"VoiceStart\": 159990, \"VoiceEnd\": 160840, \"Speaker\": \"SPK_2\", \"text\": \"ยินยอมค่ะ\" }, { \"StartTime\": 161170, \"EndTime\": 168680, \"VoiceStart\": 161170, \"VoiceEnd\": 168680, \"Speaker\": \"SPK_1\", \"text\": \"ข้อที่ สอง ข้าพเจ้ายินยอมให้บริษัทเก็บรวบรวมและใช้ข้อมูลส่วนบุคคลได้แก่ชื่อนามสกุลหมายเลขโทรศัพท์\" }, { \"StartTime\": 168900, \"EndTime\": 198730, \"VoiceStart\": 168900, \"VoiceEnd\": 198730, \"Speaker\": \"SPK_1\", \"text\": \"อีเมลที่อยู่เป็นต้นและข้อมูลอ่อนไหวตามที่พระราชบัญญัติคุ้มครองข้อมูลส่วนบุคคลพุทธศักราช 2,562 กำหนดข้าพเจ้าเจ้าของข้อมูลส่วนบุคคลสามารถถอนความยินยอมได้ทุกเมื่อแต่การถอนความยินยอมจะไม่กระทบซึ่งสิทธิของบริษัทในการเก็บรวบรวมใช้เปิดเผยข้อมูลส่วนบุคคลใดๆตามฐานข้อมูลทางกฎหมายอื่นภายใต้พระราชบัญญัติคุ้มครองข้อมูลส่วนบุคคลพุทธศักราช 2,562 ยินยอมหรือไม่คะ\" }, { \"StartTime\": 198980, \"EndTime\": 199680, \"VoiceStart\": 198980, \"VoiceEnd\": 199680, \"Speaker\": \"SPK_2\", \"text\": \"ยินยอมค่ะ\" }, { \"StartTime\": 200470, \"EndTime\": 206840, \"VoiceStart\": 200470, \"VoiceEnd\": 206840, \"Speaker\": \"SPK_1\", \"text\": \"ขั้นตอนต่อไปจะเป็นการยืนยันการซื้อประกันภัยนะคะรบกวนคุณพิมพ์ชนกตอบตกลงว่าซื้อประกันให้หน่อยค่ะ\" }, { \"StartTime\": 207070, \"EndTime\": 207720, \"VoiceStart\": 207070, \"VoiceEnd\": 207720, \"Speaker\": \"SPK_2\", \"text\": \"ได้ค่ะ\" }, { \"StartTime\": 207830, \"EndTime\": 219500, \"VoiceStart\": 207830, \"VoiceEnd\": 219500, \"Speaker\": \"SPK_1\", \"text\": \"คุณพิมพ์ชนกใจดีมีความประสงค์ที่จะซื้อประกันอุบัติเหตุกับบริษัทแอ๊บแมนประกันภัยจำกัดโดยความคุ้มครองจะเป็นไปตามรายละเอียดข้างต้นที่ได้กล่าวไว้คุณพิมพ์ชนกตกลงที่จะทำประกันหรือไม่คะ\" }, { \"StartTime\": 220250, \"EndTime\": 221690, \"VoiceStart\": 220250, \"VoiceEnd\": 221690, \"Speaker\": \"SPK_2\", \"text\": \"ตกลงทำประกันค่ะ\" }, { \"StartTime\": 221800, \"EndTime\": 251550, \"VoiceStart\": 221800, \"VoiceEnd\": 251550, \"Speaker\": \"SPK_1\", \"text\": \"ขอบคุณค่ะสำหรับเล่มกรมธรรม์จะส่งตามไปให้ไม่เกิน 7 วันทำการนะคะและถ้าหากทางคุณพิมพ์ชนกอยากทราบรายละเอียดการคุ้มครองเพิ่มเติมสามารถติดต่อดิฉันได้เลยนะคะหรือสามารถอ่านตามเล่มกรมธรรม์ที่จะจัดส่งไปที่บ้านได้เลยค่ะและหากอ่านเรียบร้อยแล้วไม่ตรงกับที่ทางเราได้แจ้งไว้สามารถบอกยกเลิกได้ภายใน 30 วันจากวันที่ได้รับกรมธรรม์นะคะขอบคุณทางคุณพิมพ์ชนกสำหรับการไว้วางใจในการซื้อประกันกับบริษัทแอ๊บแมนประกันภัยจำกัดค่ะ\" }, { \"StartTime\": 251740, \"EndTime\": 254110, \"VoiceStart\": 251740, \"VoiceEnd\": 254110, \"Speaker\": \"SPK_1\", \"text\": \"ขออนุญาตวางสายนะคะขอบคุณค่ะ\" }, { \"StartTime\": 254160, \"EndTime\": 254700, \"VoiceStart\": 254160, \"VoiceEnd\": 254700, \"Speaker\": \"SPK_2\", \"text\": \"ขอบคุณค่ะ\" } ], \"service\": \"Standard\", \"status\": \"Completed\", \"language\": \"th-TH\", \"filename\": \"Telesale-no-license\", \"date\": \"1691063707457\" }"
    # message_no_license = "{ \"sound\": \"https://mp3buckets.s3.eu-central-1.amazonaws.com/900e25ac0b0dd9fdfd6e0d0a94c39082d6b1104a09a27fa749cc11fd5767fa048038073a271b08c21ff498b14c1f88e8c8baaf6caabcbc61a36012996aaa39d5.mp3\", \"content\": [ { \"StartTime\": 1000, \"EndTime\": 4490, \"VoiceStart\": 1000, \"VoiceEnd\": 4490, \"Speaker\": \"SPK_1\", \"text\": \"สวัสดีค่ะเรียนสายอยู่กับคุณพิมพ์ชนก ใจดีใช่มั้ยขา\" }, { \"StartTime\": 4560, \"EndTime\": 6230, \"VoiceStart\": 4560, \"VoiceEnd\": 6230, \"Speaker\": \"SPK_2\", \"text\": \"ใช่ค่ะติดต่อจากไหนคะ\" }, { \"StartTime\": 6290, \"EndTime\": 12570, \"VoiceStart\": 6290, \"VoiceEnd\": 12570, \"Speaker\": \"SPK_1\", \"text\": \"ดิฉันนางสาวกนกพร ร่ำรวยนะคะตัวแทนจากบริษัทแอพแมนประกันภัยจำกัดค่ะสะดวกเป็นสายสักคู่\" }, { \"StartTime\": 12580, \"EndTime\": 14510, \"VoiceStart\": 12580, \"VoiceEnd\": 14510, \"Speaker\": \"SPK_2\", \"text\": \"ไหมค่ะได้ค่ะ\" }, { \"StartTime\": 14720, \"EndTime\": 20890, \"VoiceStart\": 14720, \"VoiceEnd\": 20890, \"Speaker\": \"SPK_1\", \"text\": \"ขอประทานโทษนะคะปกติคุณพิมพ์ชนกอ่ะค่ะเดินทางด้วยรถส่วนตัวหรือรถสาธารณะค่ะ\" }, { \"StartTime\": 21340, \"EndTime\": 23070, \"VoiceStart\": 21340, \"VoiceEnd\": 23070, \"Speaker\": \"SPK_2\", \"text\": \"เป็นรถยนต์ส่วนตัวค่ะ\" }, { \"StartTime\": 23150, \"EndTime\": 31530, \"VoiceStart\": 23150, \"VoiceEnd\": 31530, \"Speaker\": \"SPK_1\", \"text\": \"ดีเลยค่ะตอนนี้ทางเรานะคะมีประกันอุบัติเหตุมานำเสนอค่ะซึ่งจะคุ้มครองเมื่อเสียชีวิตหรือพิการจากอุบัติเหตุฆาตกรรมรอบทำร้าย\" }, { \"StartTime\": 31720, \"EndTime\": 50010, \"VoiceStart\": 31720, \"VoiceEnd\": 50010, \"Speaker\": \"SPK_1\", \"text\": \"ขับขี่โดยสารรถจักรยานยนต์และจากการก่อการร้ายค่ะตัวนี้อะค่ะครอบคลุมถึงอุบัติเหตุที่เกิดจากยานยนต์สาธารณะและยานยนต์ส่วนตัวค่ะซึ่งเงินช่วยเหลือค่าปลงศพค่ะกรณีเสียชีวิตจากอุบัติเหตุและค่ารักษาพยาบาลไม่จำกัดจำนวนครั้งอุบัติเหตุโดยค่ารักษา\" }, { \"StartTime\": 50750, \"EndTime\": 66740, \"VoiceStart\": 50750, \"VoiceEnd\": 66740, \"Speaker\": \"SPK_1\", \"text\": \"ต่ออุบัติเหตุค่ะไม่เกินทุนที่กำหนดสูงสุด 100,000 บาทจ่ายเพิ่มอีก หนึ่ง เท่าจากอุบัติเหตุที่เกิดในวันหยุดราชการรวมถึงวันเสาร์อาทิตย์หรือจ่ายเพิ่มอีก หนึ่ง เท่าจากอุบัติเหตุขณะโดยสารยานยนต์สาธารณะคุณพิมพ์ชนกมีความคิดเห็นอย่างไรบ้างคะ\" }, { \"StartTime\": 67130, \"EndTime\": 68920, \"VoiceStart\": 67130, \"VoiceEnd\": 68920, \"Speaker\": \"SPK_2\", \"text\": \"เออน่าสนใจดีนะค่ะ\" }, { \"StartTime\": 69050, \"EndTime\": 72960, \"VoiceStart\": 69050, \"VoiceEnd\": 72960, \"Speaker\": \"SPK_1\", \"text\": \"เอ่อขอโทษนะคะไม่ทราบว่าตอนนี้อ่ะคะคุณพิมพ์ชนกอายุเท่าไหร่คะ\" }, { \"StartTime\": 73010, \"EndTime\": 74080, \"VoiceStart\": 73010, \"VoiceEnd\": 74080, \"Speaker\": \"SPK_2\", \"text\": \"25 ค่ะ\" }, { \"StartTime\": 74170, \"EndTime\": 82230, \"VoiceStart\": 74170, \"VoiceEnd\": 82230, \"Speaker\": \"SPK_1\", \"text\": \"อายุ 25 ใช่ไหมคะตอนนี้ค่าเบี้ยประกันนะคะจะอยู่ที่ 3,000 บาทนะคะตกเดือนละ 250 บาทคะหรือวันละ 9 บาทเท่านั้นเองค่ะ\" }, { \"StartTime\": 82340, \"EndTime\": 83880, \"VoiceStart\": 82340, \"VoiceEnd\": 83880, \"Speaker\": \"SPK_1\", \"text\": \"คุณพิมพ์ชนกสนใจไหมคะ\" }, { \"StartTime\": 84610, \"EndTime\": 88460, \"VoiceStart\": 84610, \"VoiceEnd\": 88460, \"Speaker\": \"SPK_2\", \"text\": \"อืมถ้าสนใจทำประกันนี้ต้องดำเนินการยังไงต่อบ้างคะ\" }, { \"StartTime\": 88630, \"EndTime\": 93480, \"VoiceStart\": 88630, \"VoiceEnd\": 93480, \"Speaker\": \"SPK_1\", \"text\": \"คุณพิมพ์ชนกสะดวกชำระค่าเบี้ยราคาจ่ายทั้งหมดหรือว่าชำระเป็นรายเดือนค่ะ\" }, { \"StartTime\": 93930, \"EndTime\": 95520, \"VoiceStart\": 93930, \"VoiceEnd\": 95520, \"Speaker\": \"SPK_2\", \"text\": \"เป็นแบบรายเดือนค่ะ\" }, { \"StartTime\": 95830, \"EndTime\": 98370, \"VoiceStart\": 95830, \"VoiceEnd\": 98370, \"Speaker\": \"SPK_1\", \"text\": \"เอ่อจะเป็นการตัดผ่านบัตรเครดิตหรือว่าเงินสดคะ\" }, { \"StartTime\": 98380, \"EndTime\": 100000, \"VoiceStart\": 98380, \"VoiceEnd\": 100000, \"Speaker\": \"SPK_2\", \"text\": \"เงินสดค่ะ\" }, { \"StartTime\": 100010, \"EndTime\": 105900, \"VoiceStart\": 100010, \"VoiceEnd\": 105900, \"Speaker\": \"SPK_1\", \"text\": \"ได้ค่ะเดี๋ยวทางเราจะทำการส่งคิวอาร์โค้ดให้กับทางคุณพิมพ์ชนกนะคะหลังจบการสนทนา\" }, { \"StartTime\": 105910, \"EndTime\": 107270, \"VoiceStart\": 105910, \"VoiceEnd\": 107270, \"Speaker\": \"SPK_2\", \"text\": \"ค่ะได้ค่ะ\" }, { \"StartTime\": 107310, \"EndTime\": 115840, \"VoiceStart\": 107310, \"VoiceEnd\": 115840, \"Speaker\": \"SPK_1\", \"text\": \"โอเคค่ะต่อไปจะเป็น policy ของทางบริษัทนะคะขออนุญาตให้ข้อมูลเพิ่มเติมค่ะกระบวนการจะมีการยินยอม สอง ส่วนด้วยกันนะคะโดยส่วนที่ หนึ่ง นะคะ\" }, { \"StartTime\": 116000, \"EndTime\": 134710, \"VoiceStart\": 116000, \"VoiceEnd\": 134710, \"Speaker\": \"SPK_1\", \"text\": \"จะยินยอมให้กับทางบริษัทเก็บรวบรวมใช้และเปิดเผยข้อมูลส่วนบุคคล สอง ยินยอมให้ใช้ข้อมูลเพื่อการตลาดทางตรงและการส่งเสริมการขายค่ะข้อที่ หนึ่ง นะคะรบกวนคุณพิมพ์ชนกนะคะตอบยินยอมนะคะแล้วก็ในส่วนของข้อที่ สอง สามารถตอบยินยอมหรือไม่ยินยอมก็ได้นะคะ\" }, { \"StartTime\": 134990, \"EndTime\": 135280, \"VoiceStart\": 134990, \"VoiceEnd\": 135280, \"Speaker\": \"SPK_2\", \"text\": \"ค่ะ\" }, { \"StartTime\": 136350, \"EndTime\": 159760, \"VoiceStart\": 136350, \"VoiceEnd\": 159760, \"Speaker\": \"SPK_1\", \"text\": \"ข้อที่ หนึ่ง ค่ะข้าพเจ้ายินยอมที่จะเปิดเผยข้อมูลสุขภาพและประวัติการรักษาพยาบาลของข้าพเจ้าทั้งหมดโดยสิ้นเชิงให้แก่บริษัทแอพแมนประกันภัยจำกัดตัวแทนประกันภัยของบริษัทหรือผู้แทนของบริษัทเพื่อทำการขอเอาประกันภัยการจ่ายเงินตามกรมธรรม์ประกันภัยหรือดำเนินการใดๆที่เกี่ยวข้องกับกรมธรรม์ประกันภัยยินยอมหรือไม่คะ\" }, { \"StartTime\": 159990, \"EndTime\": 160840, \"VoiceStart\": 159990, \"VoiceEnd\": 160840, \"Speaker\": \"SPK_2\", \"text\": \"ยินยอมค่ะ\" }, { \"StartTime\": 161170, \"EndTime\": 168680, \"VoiceStart\": 161170, \"VoiceEnd\": 168680, \"Speaker\": \"SPK_1\", \"text\": \"ข้อที่ สอง ข้าพเจ้ายินยอมให้บริษัทเก็บรวบรวมและใช้ข้อมูลส่วนบุคคลได้แก่ชื่อนามสกุลหมายเลขโทรศัพท์\" }, { \"StartTime\": 198980, \"EndTime\": 199680, \"VoiceStart\": 198980, \"VoiceEnd\": 199680, \"Speaker\": \"SPK_2\", \"text\": \"ยินยอมค่ะ\" }, { \"StartTime\": 200470, \"EndTime\": 206840, \"VoiceStart\": 200470, \"VoiceEnd\": 206840, \"Speaker\": \"SPK_1\", \"text\": \"ขั้นตอนต่อไปจะเป็นการยืนยันการซื้อประกันภัยนะคะรบกวนคุณพิมพ์ชนกตอบตกลงว่าซื้อประกันให้หน่อยค่ะ\" }, { \"StartTime\": 207070, \"EndTime\": 207720, \"VoiceStart\": 207070, \"VoiceEnd\": 207720, \"Speaker\": \"SPK_2\", \"text\": \"ได้ค่ะ\" }, { \"StartTime\": 207830, \"EndTime\": 219500, \"VoiceStart\": 207830, \"VoiceEnd\": 219500, \"Speaker\": \"SPK_1\", \"text\": \"คุณพิมพ์ชนกใจดีมีความประสงค์ที่จะซื้อประกันอุบัติเหตุกับบริษัทแอ๊บแมนประกันภัยจำกัดโดยความคุ้มครองจะเป็นไปตามรายละเอียดข้างต้นที่ได้กล่าวไว้คุณพิมพ์ชนกตกลงที่จะทำประกันหรือไม่คะ\" }, { \"StartTime\": 220250, \"EndTime\": 221690, \"VoiceStart\": 220250, \"VoiceEnd\": 221690, \"Speaker\": \"SPK_2\", \"text\": \"ตกลงทำประกันค่ะ\" }, { \"StartTime\": 221800, \"EndTime\": 251550, \"VoiceStart\": 221800, \"VoiceEnd\": 251550, \"Speaker\": \"SPK_1\", \"text\": \"ขอบคุณค่ะสำหรับเล่มกรมธรรม์จะส่งตามไปให้ไม่เกิน 7 วันทำการนะคะและถ้าหากทางคุณพิมพ์ชนกอยากทราบรายละเอียดการคุ้มครองเพิ่มเติมสามารถติดต่อดิฉันได้เลยนะคะหรือสามารถอ่านตามเล่มกรมธรรม์ที่จะจัดส่งไปที่บ้านได้เลยค่ะและหากอ่านเรียบร้อยแล้วไม่ตรงกับที่ทางเราได้แจ้งไว้สามารถบอกยกเลิกได้ภายใน 30 วันจากวันที่ได้รับกรมธรรม์นะคะขอบคุณทางคุณพิมพ์ชนกสำหรับการไว้วางใจในการซื้อประกันกับบริษัทแอ๊บแมนประกันภัยจำกัดค่ะ\" }, { \"StartTime\": 251740, \"EndTime\": 254110, \"VoiceStart\": 251740, \"VoiceEnd\": 254110, \"Speaker\": \"SPK_1\", \"text\": \"ขออนุญาตวางสายนะคะขอบคุณค่ะ ไอเหี้ย\" }, { \"StartTime\": 254160, \"EndTime\": 254700, \"VoiceStart\": 254160, \"VoiceEnd\": 254700, \"Speaker\": \"SPK_2\", \"text\": \"ขอบคุณค่ะ\" } ], \"service\": \"Standard\", \"status\": \"Completed\", \"language\": \"th-TH\", \"filename\": \"Telesale-no-license\", \"date\": \"1691063707457\" }"
    speakers = []
    startTimes = []
    texts = []
    all_conv = ""
    person = ""
    if name == "Telesale-completed.m4a":
        data = json.loads(message_completed)
    elif name == "Telesale-no-license.m4a":
        data = json.loads(message_no_license)
    else:
        data = json.loads(message_completed)
    # if 'transcribed' not in st.session_state:

    # text1 = st.text_area(
    #     label="Transcript",
    #     value=value,
    #     height=300,
    # )
    
    for content in data['content']:
        if content['Speaker'] == "SPK_1":
             speakers.append("Agent")
             person = "Agent"
        elif content['Speaker'] == "SPK_2":
            speakers.append("Customer")
            person = "Customer"
        else:
            person = speakers.append(content['Speaker'])
            person = content['Speaker']

        a = timedelta(milliseconds=content['StartTime'])
        startTimes.append(str(a))
        texts.append(content['text'])
        all_conv = all_conv + person + " : " + str(content['text']) + "\n"

    # print(all_conv)
    df = pd.DataFrame(
        {
            "speaker": speakers,
            "startTime": startTimes,
            "text": texts
        }
    )

    st.dataframe(
        df,
        column_config={
            "speaker": "Speaker",
            "startTime": st.column_config.TimeColumn(
                "Conv. Time",
                format="HH:mm:ss"
            ),
            "text": st.column_config.Column(
                "Conversation",
                width="large"
            )
        },
        width=1400,
        hide_index=True,
    )

    analyze_button = st.button("Analyze Transcript")
    if analyze_button:
        # if score < 4: st.error(f"ประเมินคะแนนความพึงพอใจ: {score}")
        # elif score < 7: st.warning(f"ประเมินคะแนนความพึงพอใจ: {score}")
        # else: st.success(f"ประเมินคะแนนความพึงพอใจ: {score}")

        with st.spinner('Assessing...'):
            kwargs = { 
                "temperature": 0,
                "frequency_penalty": 0,
                "presence_penalty": 0,
                "max_tokens": 2048,
                "top_p": 1
            }
            prompt = "When telesalses calling to customer to present prodcut details, it might not process following policy's company. So,we have score 100 and separate a score in each topic depend on important and align with policy. Regarding, policy must do following  1. KYC : Telesales must know your customer, tell the correct name and also tell the customer that where calling from(score 10) 2. introduction : Telesales must always be introduce yourself by name, surname and agent license number. The agent licesnse number is a key point of this topic if no present then always return false, if only the name and surnames are provided, deduce score 15(score 20). 3.product : offer the deal or give a product detail correctly(score 40). 4.Politeness : Telesales should always be polite to customer and use no rude words such as foul language. If any rudeness is found, return False(score 20). 5.PDPA : Informed customer to request data collection(score 10). Output the analysis information in a JSON format with value true or false only. If agent didn't following the policy in each topic return false in each topic also put the explaination about why do you give a score on determine key in JSON format. Result should be in json format only with no text before and after json format. Here is the example template: {\\\"KYC\\\": true,\\\"introduction\\\": false,\\\"product\\\": true,\\\"politeness\\\": false,\\\"PDPA\\\": false,\\\"score\\\": 88,\\\"determine\\\": \\\"explain that why do you give score\\\"} I will give you a conversation which separate between agent and customer here: \\n\\n %s"
            # prompt = "When telesalses calling to customer to present prodcut details, it might not process following policy's company. Regarding, policy must do following  1. KYC : Telesales must know your customer, tell the correct name and also tell the customer that where calling from, this topic maximum score is 10. 2. Introduce_yourself : this topic maximum score is 20, telesales must always be introduce yourself by name, surname and agent license number. The agent licesnse number is a key point of this topic if no present then always return false and 0 score, if only the name and surnames are provided, deduce 15 score. 3.Product_detail : Describe insurance product correctly and also offer the deal, this topic maximum score is 40. 4.Politeness : This topic maximum score is 15, Telesales should always be polite to customer and use no rude words such as foul language or informal language. If any rudeness is found, return False and 0 score. 5.PDPA : This topic maximum score is 15, telesales should be informed customer to request data collection. 6. Calculate a score as percentage for 1-5 topic by topic 1 is 10, topic 2 is 20, topic 3 is 40, topic 4 is 15 and topic 5 is 15. If some topics not clear or do not decision that folowing policy or very complex, you can estimate as percentage and deduct a score depend on topic description. Output the analysis information in a JSON format with value true or false only. If agent didn't following the policy in each topic return false in each topic. Here is the example template: {\\\"KYC\\\": true,\\\"introduce_yourself\\\": false,\\\"product_detail\\\": true,\\\"politeness\\\": false,\\\"PDPA\\\": false,\\\"score\\\": 88} Here's the given text: \\n\\n %s"
            openai_response = gen_chat(prompt % all_conv, **kwargs)
            print(openai_response)
            completion = openai_response
            if completion['choices'][0]['finish_reason'] == "content_filter":
                message = None
            else:
                completion_type = 'success'
                message = completion['choices'][0]['message']['content'] #.strip(" \n")
            st.success('Done!')
            # st.json(message)
            data = json.loads(message)
            kyc = st.checkbox('KYC', value=data['KYC'])
            introduce_yourself = st.checkbox('Agent Introduction', value=data['introduction'])
            product = st.checkbox('Product Describe', value=data['product'])
            pdpa = st.checkbox('PDPA', value=data['PDPA'])
            politeness = st.checkbox('Politeness', value=data['politeness'])
            score = data['score']
            determine = data['determine']
            if score > 85:
                st.balloons()
            st.text_area(
                label="GPT Assessment",
                value="Telesales Evaluation: " + str(score) + "\n" + determine,
                height=200,
            )

    # st.title('This is a title')
