import requests

def update_game_item_with_images():
    url = 'http://admin.btest4wohjelay.com:3000/adminsystem/server/newgamemanager/updateGamePlatfrom'
    
    # 准备表单数据
    data = {
        #'gamingPlatformName': '夺宝电子',
        #'orderNum': '0',
        #'isHotDz': '0',
        #'isRecommend': '0',
        #'isFix': '0',
        #'showType': '2',
        #'isEnable': '1',
        'gamingPlatformId': '465',
        #'platformCode': 'JDB_DZ_LHJ',
        'gamingType': '4'
    }
    
    # 准备文件
    files = {
        'conUrlFile': ('', '', 'application/octet-stream'),  # 空文件
        'icon1File': ('', '', 'application/octet-stream'),  # 空文件
        'icon2File': ('', '', 'application/octet-stream'),   # 空文件
        'icon3File': ('', '', 'application/octet-stream'),   # 空文件
        'icon4File': ('', '', 'application/octet-stream'),   # 空文件
        'icon5File': open('C:/Users/USER/Desktop/picture/5.jpg', 'rb'),  # 实际图片文件
    }
    
    headers = {
        'Authorization': '947ec3e2-7dce-4a84-8579-b8ed29f4da69',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,zh-CN;q=0.5'
    }
    
    try:
        response = requests.post(url, data=data, files=files, headers=headers, verify=False)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        return response
    except Exception as e:
        print(f"请求失败: {e}")
    finally:
        # 关闭文件
        if 'icon2File' in files and hasattr(files['icon2File'], 'close'):
            files['icon2File'].close()

# 调用函数
update_game_item_with_images()