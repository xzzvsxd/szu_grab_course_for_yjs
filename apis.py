import concurrent.futures
import json
import os
import random
import threading
import time
from collections import deque
from functools import partial
from http.cookiejar import MozillaCookieJar

import ddddocr
import js2py
import requests
from requests.cookies import RequestsCookieJar


# 生成当前时间戳
def get_timestamp():
    return str(int(time.time() * 1000))


# 获取已选课程
def getSelectedCourse():
    url = r"https://ehall.szu.edu.cn/yjsxkapp/sys/xsxkapp/xsxkCourse/loadStdCourseInfo.do?_=" + get_timestamp()
    response = requests.post(url=url, cookies=cookies)

    json_data = json.loads(response.text)
    formatted_results = []

    for i, obj in enumerate(json_data['results']):
        course_id = obj['BJDM']
        teacher_name = obj['RKJS']
        course_name = obj['KCMC']
        teaching_place = obj['PKSJDD']

        # 打印信息
        print(f"[{i + 1}]", end=" ")
        print("course_id is :", course_id)
        print("course_name is :", course_name)
        print("teacher is :", teacher_name)
        print("place and time is :", teaching_place)
        print("---------------------------------")

        # 添加到结果列表
        formatted_results.append({
            "id": course_id,
            "name": course_name,
            "teacher": teacher_name,
            "time": teaching_place
        })

    return {
        "success": True,
        "results": formatted_results,
        "raw_data": json_data
    }


# 获取可选课程
def getAllCourseInfo():
    url = r"https://ehall.szu.edu.cn/yjsxkapp/sys/xsxkapp/xsxkCourse/loadJhnCourseInfo.do?_=" + get_timestamp()
    response = requests.post(url=url, cookies=cookies)

    json_data = json.loads(response.text)
    formatted_results = []

    for i, obj in enumerate(json_data['results']):
        course_id = obj['BJDM']
        teacher_name = obj['RKJS']
        course_name = obj['KCMC']
        teaching_place = obj['PKSJDD']
        college = obj['RWKKDWMC']

        # 打印信息
        print(f"[{i + 1}]", end=" ")
        print("course_id is :", course_id)
        print("course_name is :", course_name)
        print("teacher is :", teacher_name)
        print("college is :", college)
        print("place and time is :", teaching_place)
        print("---------------------------------")

        # 添加到结果列表
        formatted_results.append({
            "id": course_id,
            "name": course_name,
            "teacher": teacher_name,
            "time": teaching_place
        })

    return {
        "success": True,
        "results": formatted_results,
        "raw_data": json_data
    }


# 获取课程信息
def getCourseInfo(courseId):
    url = r"https://ehall.szu.edu.cn/yjsxkapp/sys/xsxkapp/jxdg/info.do"
    data = {
        "bjdm": courseId,
    }
    response = requests.post(url=url, cookies=cookies, data=data)
    # print(response.text)

    return json.loads(response.text)["rwList"][0]


# 选课
def selectCourse(courseId):
    url = r"https://ehall.szu.edu.cn/yjsxkapp/sys/xsxkapp/xsxkCourse/choiceCourse.do?_=" + get_timestamp()
    data = {
        "bjdm": courseId,
        "lx": 0
    }
    response = requests.post(url=url, cookies=cookies, data=data)
    # print(response.text)

    response = json.loads(response.text)
    if response["code"] == 1:
        print(f"选课{courseId}成功")
        return True

    return response


# 退选
def cancelCourse(courseId):
    url = r"https://ehall.szu.edu.cn/yjsxkapp/sys/xsxkapp/xsxkCourse/cancelCourse.do?_=" + get_timestamp()
    data = {
        "bjdm": courseId,
    }
    response = requests.post(url=url, cookies=cookies, data=data)
    # print(response.text)

    response = json.loads(response.text)
    if response["code"] == 1:
        print(f"退课{courseId}成功")
        return True

    return False


# 获取选课相关公告信息
def get_course_info():
    try:
        # 发送GET请求
        response = requests.get("https://ehall.szu.edu.cn/yjsxkapp/sys/xsxkapp/xsxkHome/loadPublicInfo.do")

        # 确保请求成功
        response.raise_for_status()

        # 解析JSON数据
        data = response.json()

        # 提取lcxx中的MC和KFKSSJ
        lcxx = data.get('lcxx', {})
        mc = lcxx.get('MC', '')
        kfkssj = lcxx.get('KFKSSJ', '')

        # 组合成字符串
        result = f"{mc} 开放时间: {kfkssj}"
        return result

    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        return ""
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        return ""


# 登录
def login(StudentID, Password, max_retries=5, retry_delay=2):
    for attempt in range(max_retries):
        url = r"https://ehall.szu.edu.cn/yjsxkapp/sys/xsxkapp/login/check/login.do?timestamp=" + get_timestamp()
        vtoken = get_vtoken_simple()
        result = getvtokenPicResult(vtoken)

        data = {
            "loginName": StudentID,
            "loginPwd": pwd_enc_simple(Password),
            "verifyCode": result,
            "vtoken": vtoken
        }
        response = requests.post(url=url, data=data)

        try:
            response_json = json.loads(response.text)

            if response_json["code"] == "1":
                # 登录成功后，response.cookies将包含登录后设置的Cookie
                global cookies
                cookies = response.cookies

                # # 将Cookie转换为MozillaCookieJar对象
                # cookie_jar = MozillaCookieJar()
                # for cookie in cookies:
                #     cookie_jar.set_cookie(cookie)
                # # 将Cookie保存到文件
                # cookie_jar.save('cookies.txt', ignore_discard=True, ignore_expires=True)

                print(f"登录成功，尝试次数：{attempt + 1}")
                return True
            # else:
            #     print(f"登录失败，尝试次数：{attempt + 1}，错误信息：{response_json.get('msg', '未知错误')}")
        except json.JSONDecodeError:
            # print(f"登录失败，尝试次数：{attempt + 1}，无法解析响应")
            pass
        except Exception as e:
            # print(f"登录失败，尝试次数：{attempt + 1}，发生错误：{str(e)}")
            pass

        if attempt < max_retries - 1:
            # print(f"等待 {retry_delay} 秒后重试...")
            time.sleep(retry_delay)

    print("登录失败，已达到最大重试次数")
    return False


# 密码加密算法
def pwd_enc_simple(pwd):
    url = r"https://ehall.szu.edu.cn/yjsxkapp/sys/xsxkapp/public/des.min.js"
    response = requests.get(url=url)
    js_code = response.text

    # 解析 JavaScript 代码
    context = js2py.EvalJs()
    context.execute(js_code)

    return context.DES.strEncSimple(pwd)


# 获取 vtoken
def get_vtoken_simple():
    indexBS_url = r"https://ehall.szu.edu.cn/yjsxkapp/sys/xsxkapp/public/indexBS.js"
    indexBS_response = requests.get(url=indexBS_url)
    indexBS_code = indexBS_response.text

    # 创建一个模拟的浏览器环境
    mock_browser_env = """
        var window = {};
        var document = {};
        var $ = {};
        var BH_UTILS = {};
        var BaseUrl = "https://ehall.szu.edu.cn/yjsxkapp";

        $.Deferred = function() {
            return {
                resolve: function(data) {},
                reject: function(error) {},
                promise: function() { return this; }
            };
        };

        $.extend = function() {
            var target = arguments[0];
            for (var i = 1; i < arguments.length; i++) {
                var source = arguments[i];
                for (var key in source) {
                    if (source.hasOwnProperty(key)) {
                        target[key] = source[key];
                    }
                }
            }
            return target;
        };

        $.ajax = function(options) {
            var url = options.url;
            var method = options.type || 'GET';  // 默认为 GET
            var data = options.data || {};
            var headers = options.headers || {};

            var response = sendRequest(url, method, data, headers);

            if (response.ok) {
                if (typeof options.success === 'function') {
                    options.success(response.data);
                }
            } else {
                if (typeof options.error === 'function') {
                    options.error({
                        status: response.status,
                        responseText: response.text
                    });
                }
            }

            return response.data;
        };

        BH_UTILS.doAjax = function (url, params, method, requestOption, headers) {
            requestOption = requestOption || {};
            var ajaxOptions = $.extend({}, {
                type: method || 'POST',
                url: url,
                data: params || {},
                headers : headers || {},
                dataType: 'json',
                success: function (resp) {},
                error: function (resp) {}
            }, requestOption);

            return $.ajax(ajaxOptions);
        };
    """

    def send_request(url, method, data, headers):
        try:
            # print('send_request: ', url, method, data, headers)

            url = str(url)
            # 检查并去掉不必要的引号
            if url.startswith("'") and url.endswith("'"):
                url = url[1:-1]

            headers_tmp = {
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0',
            }

            response = requests.get(url, headers=headers_tmp)
            # print('response: ', response.ok, response.status_code, response.text)
            return {
                'ok': response.ok,
                'status': response.status_code,
                'data': response.json() if response.ok else None,
                'text': response.text
            }
        except Exception as e:
            return {
                'ok': False,
                'status': 0,
                'data': None,
                'text': str(e)
            }

    def print_to_python(message):
        print(message)

    # 创建 JavaScript 执行环境
    context = js2py.EvalJs({
        'sendRequest': send_request,
        'print_to_python': print_to_python
    })

    # 执行模拟的浏览器环境
    context.execute(mock_browser_env)

    # 执行 JavaScript 文件
    context.execute(indexBS_code)

    # 调用 queryVocdeToken 函数
    response = context.queryVocdeToken().to_dict()
    # print(response)
    if response['code'] == '1':
        return response['data']['token']

    return None


# 获取验证码图片 & 识别验证码图片
def getvtokenPicResult(vtoken):
    url = r'https://ehall.szu.edu.cn/yjsxkapp/sys/xsxkapp/login/vcode/image.do?vtoken=' + vtoken
    response = requests.get(url=url)
    # 检查请求是否成功
    if response.status_code == 200:
        ocr = ddddocr.DdddOcr(show_ad=False)
        result = ocr.classification(response.content)
        # print(result)

        if len(result) != 4:
            return None

        return result
    else:
        print(f"Failed to retrieve image. Status code: {response.status_code}")
        return None


# 从文件加载Cookie
def load_cookies_from_file():
    cookie_jar = MozillaCookieJar()
    cookie_jar.load('cookies.txt', ignore_discard=True, ignore_expires=True)

    # 创建一个新的 RequestsCookieJar 实例
    requests_cookiejar = RequestsCookieJar()

    # 将 MozillaCookieJar 中的 cookie 添加到 RequestsCookieJar
    for cookie in cookie_jar:
        requests_cookiejar.set(cookie.name, cookie.value, domain=cookie.domain, path=cookie.path)

    return requests_cookiejar


# 创建一个消息队列
successful_courses = set()
message_queue = deque(maxlen=100)  # 限制队列最大长度为100


def add_message(message, type="info"):
    """添加消息到队列"""
    print(f"[{type}] {message}")
    message_queue.append({
        "message": message,
        "type": type,  # "info", "success", "error"
        "timestamp": time.time()
    })


def select_course_wrapper(course, config_setting):
    api_wrapper = Api()
    try:
        # 检查速率限制
        can_request, message = api_wrapper.check_rate_limits()
        if not can_request:
            add_message(f"{message}", "error")
            time.sleep(config_setting.get('delay', 2))
            return False

        response = selectCourse(course["id"])
        api_wrapper.record_request()  # 记录请求

        if response is True:
            add_message(f"{course['name']}  {course['teacher']}  抢课成功", "success")
            return True
        else:
            message = response['msg'].split(' ')[0]
            add_message(f"{course['name']}: {message}", "error")

            # 检查频繁操作的提示
            if "您的操作过于频繁" in response['msg']:
                delay_time = random.uniform(10, 30)
                add_message(f"检测到频繁操作，随机延时 {delay_time:.2f} 秒", "info")
                time.sleep(delay_time)
            else:
                time.sleep(config_setting.get('delay', 2))
            return False
    except Exception as e:
        add_message(f"抢课 {course['name']} 时出错: {str(e)}", "error")
        return False


def concurrent_course_selection(course_list, config_setting, should_stop):
    max_workers = config_setting.get('max_workers', 4)
    count = config_setting.get('count', 100)
    delay = config_setting.get('delay', 2)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        for round in range(count):
            if should_stop():
                add_message("抢课已取消", "info")
                return False

            add_message(f"开始第 {round + 1} 轮抢课...", "info")

            remaining_courses = [course for course in course_list if course['id'] not in successful_courses]

            if not remaining_courses:
                add_message("所有课程已抢到，结束抢课", "success")
                return True

            select_course_partial = partial(select_course_wrapper, config_setting=config_setting)
            futures = [executor.submit(select_course_partial, course) for course in remaining_courses]

            for future, course in zip(concurrent.futures.as_completed(futures), remaining_courses):
                if should_stop():
                    add_message("抢课已取消", "info")
                    return False
                if future.result():
                    successful_courses.add(course['id'])

            add_message(f"第 {round + 1} 轮抢课结束，已抢到 {len(successful_courses)} 门课程", "info")
            if round < count - 1 and not should_stop():
                add_message(f"等待下一轮...", "info")
                time.sleep(delay / 1000.0)

    return len(successful_courses) == len(course_list)


class Api:
    def __init__(self):
        self.CONFIG_FILE = 'config.json'
        self.cookies = None
        self.selection_thread = None
        self.stop_selection = False
        self.config = self.load_config()
        self.course_info = get_course_info()
        self.cleanup_rate_tracking()

    def cleanup_rate_tracking(self):
        """清理过期的请求记录"""
        current_time = time.time()

        # 如果没有rate_tracking字段，添加它
        if 'rate_tracking' not in self.config:
            self.config['rate_tracking'] = {
                'hourly_requests': [],
                'short_term_requests': [],
                'last_cleanup': current_time
            }

        # 清理超过1小时的记录
        hour_ago = current_time - 3600
        self.config['rate_tracking']['hourly_requests'] = [
            ts for ts in self.config['rate_tracking']['hourly_requests']
            if ts > hour_ago
        ]

        # 清理超过短期窗口的记录
        window_ago = current_time - self.config['settings'].get('rate_limits', {}).get('short_term_window', 5)
        self.config['rate_tracking']['short_term_requests'] = [
            ts for ts in self.config['rate_tracking']['short_term_requests']
            if ts > window_ago
        ]

        self.config['rate_tracking']['last_cleanup'] = current_time
        self.save_config()

    def check_rate_limits(self):
        """检查是否超过速率限制"""
        self.cleanup_rate_tracking()

        # 获取限制设置
        rate_limits = self.config['settings'].get('rate_limits', {
            'hourly_limit': 1000,
            'short_term_limit': 10,
            'short_term_window': 5
        })

        # 检查小时限制
        hourly_count = len(self.config['rate_tracking']['hourly_requests'])
        if hourly_count >= rate_limits['hourly_limit']:
            return False, "已达到每小时请求限制"

        # 检查短期限制
        short_term_count = len(self.config['rate_tracking']['short_term_requests'])
        if short_term_count >= rate_limits['short_term_limit']:
            return False, "请求过于频繁，请稍后再试"

        return True, ""

    def record_request(self):
        """记录一次请求"""
        current_time = time.time()
        self.config['rate_tracking']['hourly_requests'].append(current_time)
        self.config['rate_tracking']['short_term_requests'].append(current_time)
        self.save_config()

    def get_initial_data(self):
        return self.course_info

    def get_messages(self, last_timestamp=0):
        """获取新消息"""
        messages = []
        for msg in message_queue:
            if msg["timestamp"] > last_timestamp:
                messages.append(msg)
        return messages

    def load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {
                "credentials": {"student_id": "", "password": ""},
                "settings": {"delay": 1, "max_workers": 5, "count": 100},
                "selected_courses": []
            }
        except Exception:
            return {
                "credentials": {"student_id": "", "password": ""},
                "settings": {"delay": 1, "max_workers": 5, "count": 100},
                "selected_courses": []
            }

    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置文件失败: {str(e)}")

    def login(self, student_id, password):
        try:
            login_result = login(student_id, password)
            if login_result:
                # 保存登录凭证
                self.config["credentials"]["student_id"] = student_id
                self.config["credentials"]["password"] = password
                self.save_config()
                return {"success": True, "message": "登录成功"}
            return {"success": False, "message": "登录失败"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def start_selection(self, course_ids, delay, max_workers):
        if self.selection_thread and self.selection_thread.is_alive():
            self.stop_selection = True
            return {"success": True, "message": "正在停止抢课...", "status": "stopping"}

        self.stop_selection = False

        # 保存课程信息和设置
        self.config["settings"]["delay"] = delay
        self.config["settings"]["max_workers"] = max_workers
        self.config["settings"]["count"] = self.config["settings"].get("count", 100)
        self.config["selected_courses"] = course_ids
        self.save_config()

        def run_selection():
            config_setting = {
                'delay': delay,
                'max_workers': max_workers,
                'count': self.config["settings"].get("count", 100)
            }

            course_list = []
            for course_id in course_ids:
                course_info = getCourseInfo(course_id)
                course_list.append({
                    "id": course_id,
                    "name": course_info['KCMC'],
                    "teacher": course_info['RKJS']
                })

            try:
                result = concurrent_course_selection(course_list, config_setting, lambda: self.stop_selection)
                status = "stopped" if self.stop_selection else "completed"
                return {"success": result, "message": "抢课完成", "status": status}
            except Exception as e:
                return {"success": False, "message": str(e), "status": "error"}

        self.selection_thread = threading.Thread(target=run_selection)
        self.selection_thread.start()
        return {"success": True, "message": "抢课任务已启动", "status": "running"}

    def get_saved_credentials(self):
        """获取保存的登录信息"""
        return self.config["credentials"]

    def get_saved_courses(self):
        """获取保存的课程信息"""
        return {
            "courses": self.config["selected_courses"],
            "settings": self.config["settings"]
        }

    def save_selected_courses(self, course_ids):
        """保存选定的课程"""
        try:
            self.config["selected_courses"] = course_ids
            self.save_config()
            return {"success": True, "message": "保存成功"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_available_courses(self):
        try:
            response = getAllCourseInfo()
            if response['success']:
                courses = list(response['results'])
                return courses
            return []
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_selected_courses(self):
        try:
            response = getSelectedCourse()
            if response['success']:
                courses = list(response['results'])
                return courses
            return []
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_course_info(self, course_id):
        try:
            course_info = getCourseInfo(course_id)
            return {
                "success": True,
                "data": {
                    "id": course_id,
                    "name": course_info['KCMC'],
                    "teacher": course_info['RKJS'],
                    "time": course_info['PKSJDD']
                }
            }
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_selection_status(self):
        if self.selection_thread and self.selection_thread.is_alive():
            return {"running": True, "stopping": self.stop_selection}
        return {"running": False, "stopping": False}


if __name__ == "__main__":
    StudentID = input("请输入学号: ")
    Password = input("请输入密码: ")
    Api().login(StudentID, Password)
    getAllCourseInfo()
