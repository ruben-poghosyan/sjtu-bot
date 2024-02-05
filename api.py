import enum
import itertools
import requests
from datetime import datetime


class Degree(enum.Enum):
    BS = 0,
    MS = 1,
    PHD = 3


class Course:
    def __init__(self, code: str, schedule: list) -> None:
        self.code = code
        self.schedule = schedule

    def set_name(self, name):
        self.name = name


class User:
    def __init__(self, cookie: str = "") -> None:
        self.cookie = {"XK_TOKEN": cookie}
        self.degree = Degree.MS
        if cookie:
            self.load()
        else:
            self.courses = []

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
            # TODO init selectable courses from REST api
            self.courses = []

    def _sublists(self, lst):
        temp = []
        for L in range(len(lst) + 1):
            for subset in itertools.combinations(lst, L):
                temp.append(list(subset))
        return temp

    def _is_overlap(self, task_1: list, task_2: list):
        """check if there is overal between two tasks with any number of intervals
        """
        flag = False
        for x in task_1:
            for y in task_2:
                if x[0] <= y[1] and y[0] <= x[1]:
                    flag = True
        return flag

    def _find_non_overlapping_configurations(self):
        # self.courses is a list of Course objects
        configurations = self._sublists(self.courses)
        temp = []
        for configuration in configurations:
            n = len(configuration)
            if n == 1:
                temp.append(configuration)
            else:
                flag = False
                for i in range(n - 1):
                    for j in range(i + 1, n):
                        if self._is_overlap(configuration[i].schedule, configuration[j].schedule):
                            flag = True
                            break
                if not flag:
                    temp.append(configuration)
        return temp

    def find_best_configurations(self):
        """ Basic implementation of interval scheduling
        where each task has n >= 1 mutually exclusive intervals, time complexity O(2^n), use with caution
        """
        tasks = self._find_non_overlapping_configurations()
        tasks.pop(0)
        temp = []
        max_len = len(max(tasks, key=lambda x: len(x)))
        for x in tasks:
            if len(x) == max_len:
                temp.append(x)
        return temp


if __name__ == "__main__":
    a = Course('1', [(3, 5), (7, 9)])
    b = Course('2', [(0, 1), (5, 7)])
    c = Course('3', [(2, 3), (9, 10)])
    user = User()
    user.courses.append(a)
    user.courses.append(b)
    user.courses.append(c)
    best = user.find_best_configurations()
    for (i, config) in enumerate(best):
       temp = []
       for course in config:
           temp.append(course.code) 
       print(i, temp)