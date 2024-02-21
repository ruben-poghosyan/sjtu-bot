import enum
import re
import itertools
import requests
from datetime import datetime


class Degree(enum.Enum):
    BS = 0,
    MS = 1,
    PHD = 3


class Course:
    def __init__(self, code: str, schedule: list=[]) -> None:
        self.code = code
        self.schedule = schedule
        

    def set_name(self, name):
        self.name = name
    
    def set_schedule(self, schedule: list):
        self.schedule = schedule
    
    def set_max_seats(self, n:int):
        self.max_seats = n
    
    def set_occupied_seats(self, n:int):
        self.occupied_seats = n
    
    def set_campus(self, campus:str):
        self.campus = campus
    
    def set_id(self, id:str):
        self.id = id



class User:
    def __init__(self, cookie: str = "") -> None:
        self.cookie = {"XK_TOKEN": cookie}
        self.degree = Degree.MS
        self.courses = []
        if cookie:
            self.load()

    def set_check_available(self, flag:bool):
            self.check_available = flag
            

    def load(self):
        # TODO implement loading schemes for other degrees
        if self.degree == Degree.MS:
            self.routes = ["http://yjsxk.sjtu.edu.cn/yjsxkapp/sys/wdpyjhapp/modules/wdpyjh/wdxx.do",
                      "http://yjsxk.sjtu.edu.cn/yjsxkapp/sys/wdpyjhapp/modules/wdpyjh/wdkclbtj.do",
                      "http://yjsxk.sjtu.edu.cn/yjsxkapp/sys/wdpyjhapp/modules/wdpyjh/wdkcxx.do",
                      "http://yjsxk.sjtu.edu.cn/yjsxkapp/sys/xsxkapp/xsxkHome/loadPublicInfo_index.do",
                      "http://yjsxk.sjtu.edu.cn/yjsxkapp/sys/xsxkapp/xsxkHome/loadPublicInfo_course.do",
                      "http://yjsxk.sjtu.edu.cn/yjsxkapp/sys/xsxkapp/xsxkCourse/loadJhnCourseInfo.do",
                      "http://yjsxk.sjtu.edu.cn/yjsxkapp/sys/xsxkapp/xsxkCourse/choiceCourse.do"]
            try:
                r1 = requests.get(self.routes[0], cookies=self.cookie).json()
                r2 = requests.get(self.routes[1], cookies=self.cookie).json()
                r3 = requests.get(self.routes[2], cookies=self.cookie).json()
                r4 = requests.get(self.routes[3], cookies=self.cookie).json()
                r5 = requests.get(self.routes[4], cookies=self.cookie).json()
                r6 = requests.post(self.routes[5], cookies=self.cookie, data={"pageSize":10, "pageIndex":1}).json()
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
            # this token is used to select courses
            self._csrf_token = r5['csrfToken']
            self.schedule_regex = r".\[\d+-\d+.\]"
            self.session_regex = r"[0-9]{1,}"
            self.schedule_extractor = re.compile(self.schedule_regex)
            self.session_extractor = re.compile(self.session_regex)
            self.day_map = {"一":0,"二":1,"三":2,"四":3,"五":4,"六":5, "七": 6}
            # get the selectable courses within the training plan
            for data in r6['datas']:
                schedule = []
                course = Course(data['BJMC'])
                course.set_name(data['KCDM'])
                course.set_campus(data['XQYWMC'])
                course.set_occupied_seats(data['DQRS'])
                course.set_max_seats(data['KXRS'])
                course.set_id(data['BJDM'])
                schedule_str = data.get('PKSJDD','')
                # if there is schedule, otherwise just add the course without schedule
                if schedule_str:
                    schedule_str.replace(" ", "")
                    schedule_str_array = self.schedule_extractor.findall(schedule_str)
                    for entry in schedule_str_array:
                        day = entry[0]
                        sessions = self.session_extractor.findall(entry)
                        start_session = self.day_map[day]*15 + int(sessions[0])
                        end_session = self.day_map[day]*15 + int(sessions[1])
                        schedule.append((start_session, end_session))
                    course.set_schedule(schedule)
                self.courses.append(course)
                
    def select(self, course: Course):
        url = self.routes[6]
        response = requests.post(url, cookies=self.cookie,data={"bjdm": course.id, "lx":0, "csrfToken":self._csrf_token})
        return response


    def _sublists(self, lst):
        """Generate all possible and impossible combinations of courses taking into account that one course
        can have multiple instances
        """
        final = []
        temp = []
        for L in range(len(lst) + 1):
            for subset in itertools.combinations(lst, L):
                temp.append(list(subset))
        # remove all configurations where there is a repeated course with the same name
        for configuration in temp:
            l = len(configuration)
            flag = False
            for i in range(l):
                for j in range(i+1,l):
                    if configuration[i].name == configuration[j].name:
                        flag = True
                        break
            if not flag:
                final.append(configuration)
        return final

    def _is_overlap(self, task_1: list, task_2: list):
        """check if there is overal between two tasks with any number of intervals
        """
        flag = False
        for x in task_1:
            for y in task_2:
                if x[0] <= y[1] and y[0] <= x[1]:
                    flag = True
        return flag

    def _find_non_overlapping_configurations(self, courses:list):
        # courses is a list of Course objects
        configurations = self._sublists(courses)
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
        # remove courses which don't have scedule
        self.remove_unscheduled_courses()
        # check what courses have open slots
        selectable = self.get_selectable_courses()
        tasks = self._find_non_overlapping_configurations(selectable)
        tasks.pop(0)
        temp = []
        max_len = len(max(tasks, key=lambda x: len(x)))
        for x in tasks:
            if len(x) == max_len:
                temp.append(x)
        return temp

    def print_courses(self):
        for course in self.courses:
            print(course.code, course.schedule, f"{course.occupied_seats}/{course.max_seats}")
    
    def get_unique_course_names(self):
        return set([course.name for course in self.courses])

    def get_selectable_courses(self):
        temp = []
        for course in self.courses:
            if course.max_seats - course.occupied_seats > 0:
                temp.append(course)
        return temp

    def remove_unscheduled_courses(self):
        temp = []
        for course in self.courses:
            if course.schedule:
                temp.append(course)
        self.courses = temp


if __name__ == "__main__":
    a = Course('Course 1', [(3, 4), (7, 9)])
    b = Course('Course 2', [(2, 2), (5, 6)])
    c = Course('Course 3', [(2, 3), (9, 10)])
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