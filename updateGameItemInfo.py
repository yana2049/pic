import requests

def update_game_item_with_images():
    url = 'http://admin.btest4wohjelay.com:3000/adminsystem/server/newgamemanager/updateGameItemInfo'
    
    # 准备表单数据
    data = {
        #'gamingItemName': '幸运宝石',
        #'orderNum': '0',
        #'isHotDz': '0',
        #'isRecommend': '0',
        #'isFix': '0',
        #'showType': '2',
        #'isEnable': '1',
        #'gemeDesc': '幸运宝石',
        'gamingItemId': '16177',
        'platformCode': 'JDB_DZ_LHJJ',
        "gamingItemCode": "14095",
        'gamingType': '4'
    }
    print(data)
    # 准备文件
    files = {
        'conUrlFile': ('', '', 'application/octet-stream'),  # 空文件
        'icon1File': ('', '', 'application/octet-stream'),  # 空文件
        'icon2File': open('C:/Users/USER/Desktop/picture/5.jpg', 'rb'),  # 实际图片文件
        'icon3File': ('', '', 'application/octet-stream'),   # 空文件
        #'hjConUrlFile': open('C:/Users/USER/Desktop/picture/5.jpg', 'rb'),  # 实际图片文件
        'hjIcon1File': ('', '', 'application/octet-stream'),   # 空文件
        'hjIcon2File': ('', '', 'application/octet-stream'),   # 空文件
        'hjIcon3File': ('', '', 'application/octet-stream'),   # 空文件
    }
    print(files)
    headers = {
        'Authorization': '9999e327-1b0c-4950-beae-c41ed78658ab',
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