import requests
from datetime import datetime

routes = ["http://yjsxk.sjtu.edu.cn/yjsxkapp/sys/wdpyjhapp/modules/wdpyjh/wdxx.do", "http://yjsxk.sjtu.edu.cn/yjsxkapp/sys/wdpyjhapp/modules/wdpyjh/wdkclbtj.do", "http://yjsxk.sjtu.edu.cn/yjsxkapp/sys/wdpyjhapp/modules/wdpyjh/wdkcxx.do","http://yjsxk.sjtu.edu.cn/yjsxkapp/sys/xsxkapp/xsxkHome/loadPublicInfo_index.do"]
# sign in to jaccount and grab the cookie named XK_TOKEN
cookies = {"XK_TOKEN":"f38ea3b6-1881-4474-a299-ea8de94fbfe2"}
stop = False
try:
    r1 = requests.get(routes[0], cookies=cookies).json()
    r2 = requests.get(routes[1], cookies=cookies).json()
    r3 = requests.get(routes[2], cookies=cookies).json()
    r4 = requests.get(routes[3], cookies=cookies).json()
except Exception:
    print("Token is broken, please use a new one")
    stop = True
if not stop:
    print("-"*60)
    print(f"Username: {r1['reMapData']['XSXX']['XM']}")
    print(f"User ID: {r1['reMapData']['SHZTXX']['XH']}")
    print(f"Supervisor: {r1['reMapData']['XSXX']['DSXM']}")
    print(f"Grade: {r1['reMapData']['XSXX']['NJDM']}")
    print(f"GPA (current/min): {r2['reMapData']['WCGPA']} / {r1['reMapData']['XSXX']['GPAYQ_DISPLAY']}")
    str_format = '%Y-%m-%d %H:%M:%S'
    enrollment_start = datetime.strptime(r4['lcxx']['KFKSSJ'], str_format)
    current = datetime.strptime(r4['dqsj'], str_format)
    duration = enrollment_start - current
    clock = 'open'
    if duration.days > 0:
        clock = f"{duration.days} days to open"
    else:
        clock = f"{duration.seconds/3600} hours to open"
    print(f"Course Selection System Status : {clock}")
    print("-"*60)
    print("Training Plan")
    for (i, course) in enumerate(r3['msg']):
        print(f"{i+1}: {course['KCDM']} - {course['KCMC']} - {course['XQJJ_DISPLAY']}")
    print("-"*60)
    question = input("Proceed to select courses?(y/n)")
    if question == 'y':
        if duration.seconds > 300:
            print("Please start the process 5 minutes before the course selection opens for maximum effectivity, quitting!")
        else:
            print("Courses to be selected in current semester")
            print("Waiting untill the system is open, the script will now do live-updates on selection status")
            # TODO implement after the system opens
    else:
        print("Quitting !")



