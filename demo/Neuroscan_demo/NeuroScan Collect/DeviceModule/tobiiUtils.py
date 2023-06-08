import json
import requests
import random

base_url = 'http://'

def random_str(random_length):
    string = ''
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    length = len(chars) - 1
    # random = Random()
    # 设置循环每次取一个字符用来生成随机数
    for i in range(random_length):
        string += chars[random.randint(0, length)]
    return string

def getEagleId():
    return random_str(8)+"-"+random_str(4)+"-"+random_str(4)+"-"+random_str(4)+"-"+random_str(12)

def post_project1(api_action,ip):
    url = base_url +str(ip)+ api_action
    print(url)
    headers = {
        'Content-Type': 'application/json',
    }
    response = requests.post(url=url, headers=headers)
    response = json.loads(response.text)
    return response

def post_project2(api_action,ip,id,time):
    url = base_url +str(ip)+ api_action +id
    print(url)
    eagleId = getEagleId()
    data = {'pr_id': id,
            'pr_created':time,
            'pr_info':{
                'EagleId': eagleId,
                'Name':'embemc'
            }}
    data = json.dumps(data)

    headers = {
        'Content-Type': 'application/json',
    }
    response = requests.post(url=url, data=data, headers=headers)
    response = json.loads(response.text)

    return response,eagleId


def post_participant1(api_action,ip,pid):
    url = base_url +str(ip)+ api_action
    print(url)
    data = {'pa_project': pid }
    data = json.dumps(data)
    headers = {
        'Content-Type': 'application/json',
    }
    response = requests.post(url=url, data=data, headers=headers)
    response = json.loads(response.text)
    return response

def post_participant2(api_action,ip,pid,paid):
    url = base_url +str(ip)+ api_action +"/"+paid
    print(url)
    eagleId = getEagleId()
    data = {'pa_project': pid,
            'pa_id':paid,
            'pa_info':{
                'EagleId': eagleId,
                'Name':'embemc001',
                'Notes':'test'
            }}
    data = json.dumps(data)

    headers = {
        'Content-Type': 'application/json',
    }
    response = requests.post(url=url, data=data, headers=headers)
    print(response.text)
    response = json.loads(response.text)
    return response,eagleId

def post_recording1(api_action,ip,paid):
    url = base_url +str(ip)+ api_action
    print(url)
    data = {'rec_participant': paid,
            'rec_state':'init'
            }
    data = json.dumps(data)
    headers = {
        'Content-Type': 'application/json',
    }
    response = requests.post(url=url, data=data, headers=headers)
    response = json.loads(response.text)
    return response

def post_recording2(api_action,ip,rid,paid,pid):
    url = base_url +str(ip)+ api_action +"/"+rid
    print(url)
    eagleId = getEagleId()
    data = {'rec_id': rid,
            'rec_info':{
                'EagleId': eagleId,
                'Name':'recording001',
                'Notes':'recording_test'
            },
            'rec_participant':paid,
            'rec_project':pid,
            'rec_state':'init'
            }
    data = json.dumps(data)

    headers = {
        'Content-Type': 'application/json',
    }
    response = requests.post(url=url, data=data, headers=headers)
    print(response.text)
    response = json.loads(response.text)
    return response,eagleId

def post_calibration1(api_action,ip,paid):
    url = base_url +str(ip)+ api_action
    print(url)
    data = {'ca_participant': paid,
            'ca_state':'uncalibrated',
            'ca_type':'default'
            }
    data = json.dumps(data)
    headers = {
        'Content-Type': 'application/json',
    }
    response = requests.post(url=url, data=data, headers=headers)
    print(response.text)
    response = json.loads(response.text)
    return response

def post_calibration2(api_action,ip,cid):
    url = base_url + str(ip) + api_action+"/"+cid+"/start"
    print(url)
    headers = {
        'Content-Type': 'application/json',
    }
    response = requests.post(url=url, headers=headers)
    response = json.loads(response.text)
    return response

def get_calibration_state(api_action,ip,cid):
    url = base_url + str(ip) + api_action + "/" + cid + "/status"
    print(url)
    response = requests.get(url=url)
    response = json.loads(response.text)
    return response
