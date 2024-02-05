import enum
import requests
from datetime import datetime


class Degree(enum.Enum):
    BS = 0,
    MS = 1,
    PHD = 3


class User:
    def __init__(self, cookie: str) -> None:
        self.cookie = {"XK_TOKEN": cookie}
        self.degree = Degree.MS
        self.load()

    def load(self):
        # TODO implement loading schemes for other degrees
        if self.degree == Degree.MS:
            routes = ["http://yjsxk.sjtu.edu.cn/yjsxkapp/sys/wdpyjhapp/modules/wdpyjh/wdxx.do",
                      "http://yjsxk.sjtu.edu.cn/yjsxkapp/sys/wdpyjhapp/modules/wdpyjh/wdkclbtj.do",
                      "http://yjsxk.sjtu.edu.cn/yjsxkapp/sys/wdpyjhapp/modules/wdpyjh/wdkcxx.do",
                      "http://yjsxk.sjtu.edu.cn/yjsxkapp/sys/xsxkapp/xsxkHome/loadPublicInfo_index.do"]
            try:
                r1 = requests.get(routes[0], cookies=self.cookie).json()
                r2 = requests.get(routes[1], cookies=self.cookie).json()
                r3 = requests.get(routes[2], cookies=self.cookie).json()
                r4 = requests.get(routes[3], cookies=self.cookie).json()
            except Exception:
                raise Exception("Token is broken, please use a new one")

            self.name = r1['reMapData']['XSXX']['XM']
            self.user_id = r1['reMapData']['SHZTXX']['XH']
            self.supervisor = r1['reMapData']['XSXX']['DSXM']
            self.grade = r1['reMapData']['XSXX']['NJDM']
            self.current_gpa = r2['reMapData']['WCGPA']
            self.min_gpa = r1['reMapData']['XSXX']['GPAYQ_DISPLAY']
            date_format = '%Y-%m-%d %H:%M:%S'
            self.class_enrollment_start_date = datetime.strptime(
                r4['lcxx']['KFKSSJ'], date_format)
            self.login_date = datetime.strptime(r4['dqsj'], date_format)
            self.training_plan = []
            for obj in r3['msg']:
                course = Course(obj['KCDM'])
                course.set_name(obj['KCMC'])
                self.training_plan.append(course)


class Course:
    def __init__(self, code:str) -> None:
        self.code = code
    
    def set_name(self, name):
        self.name = name
    
    def __eq__(self, other) -> bool:
        return self.code == other.code
