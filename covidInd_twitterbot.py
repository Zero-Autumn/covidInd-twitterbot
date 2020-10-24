import re
import requests
import json
import tweepy
import re
import time
#---------------------------------------------------------------------------------------
#functions
def check_availability(a,b,state_availability,district_availability,py_obj):
    for one in py_obj:
        if a in one['state'].lower() or a in one['statecode'].lower():
            state_availability=True
            for one_dis in one['districtData']:
                if b in one_dis['district'].lower():
                    district_availability=True
    return state_availability,district_availability

def search(a,b,py_obj):
    for one in py_obj:
        if a in one['state'].lower() or a in one['statecode'].lower():
            # print('State:',one['state'])
            # print()
            for one_dis in one['districtData']:
                if b in one_dis['district'].lower():
                    # print('\tDistrict:',one_dis['district'])
                    # print('\t\t Confirmed cases:',one_dis['confirmed'])
                    # print('\t\t Active cases:',one_dis['active'])
                    # print('\t\t Deceased:',one_dis['deceased'])
                    # print('\t\t Recovred:',one_dis['recovered'])
                    # print()
                    return one_dis['confirmed'],one_dis['active'],one_dis['deceased'],one_dis['recovered']
                    break
# file_path='E:\\!python course\\python projects\\last_id.txt'
file_path='last_id.txt'
def store_id(tweet_id):
    with open(file_path,'w') as f_write:
        f_write.write(str(tweet_id))

def read_id():
    with open(file_path,'r') as f_read:
        return int(f_read.read().strip())

#---------------------------------------------------------------------------------------

consumer_key=''
consumer_secret=''
access_token=''
access_token_secret=''

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


while True:
    res=requests.get('https://api.covid19india.org/v2/state_district_wise.json')
    response=res.json()
    j_obj=json.dumps(response,indent=2)
    py_obj=json.loads(j_obj)

    state_availability,district_availability=False,False
    tweet_id=None
    confirmed=active=deceased=recoverd=None

    last_id=read_id()
    mentions=api.mentions_timeline(int(last_id))
    for mention in reversed(mentions):
        state_availability,district_availability=False,False
        tweet_id=mention.id
        store_id(tweet_id)
        querry=mention.text.lower()
        pattern=r'#\S+'
        if re.search(pattern,querry,flags=re.I):
            match_obj=re.search(pattern,querry)
            text_t=match_obj.group()
            result = re.split(r'[.]', text_t)
            state_t=result[0]
            district_t=result[1]
            state_t=state_t[1:]
            state_input=re.sub('_',' ',state_t).lower()
            district_input=re.sub('_',' ',district_t).lower()
            state_availability,district_availability=check_availability(state_input,district_input,state_availability,district_availability,py_obj)
            if state_availability==True and district_availability==True:
                confirmed,active,deceased,recoverd=search(state_input,district_input,py_obj)
                at=mention.user.screen_name
                state=state_input.capitalize()
                district=district_input.capitalize()
                api.update_status(f'@{at} \t{state} : {district}\nConfirmed:{confirmed}\nActive:{active}\nDeceased:{deceased}\nRecovered:{recoverd}\nStay Safe!',mention.id)
                

            elif state_availability==False:
                at=mention.user.screen_name
                api.update_status(f'@{at} couldnt find the requested State or the State code, check bio for more info',mention.id)
                #print('couldnt find the requested State or the State code.There might be a spelling mistake! try again with the correct spelling')
            elif district_availability==False:
                at=mention.user.screen_name
                api.update_status(f'@{at} couldnt find the requested District, you might have made a spelling mistake, check bio for more info',mention.id)
                #print('couldnt find the requested district.There might be a spelling mistake! try again with the correct spelling')
    time.sleep(15)        
