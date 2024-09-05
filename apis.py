import json
import time
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
    # print(response.text)

    json_data = json.loads(response.text)
    # print(json_data['dataList'])
    for i, obj in enumerate(json_data['results']):
        course_id = obj['BJDM']
        teacher_name = obj['RKJS']
        course_name = obj['KCMC']
        teaching_place = obj['PKSJDD']

        print(f"[{i + 1}]", end=" ")
        print("course_id is :", course_id)
        print("course_name is :", course_name)
        print("teacher is :", teacher_name)
        print("place and time is :", teaching_place)
        print("---------------------------------")


# 获取可选课程
def getAllCourseInfo():
    url = r"https://ehall.szu.edu.cn/yjsxkapp/sys/xsxkapp/xsxkCourse/loadJhnCourseInfo.do?_=" + get_timestamp()
    response = requests.post(url=url, cookies=cookies)
    # print(response.text)

    json_data = json.loads(response.text)
    # print(json_data['dataList'])
    for i, obj in enumerate(json_data['results']):
        course_id = obj['BJDM']
        teacher_name = obj['RKJS']
        course_name = obj['KCMC']
        teaching_place = obj['PKSJDD']

        print(f"[{i + 1}]", end=" ")
        print("course_id is :", course_id)
        print("course_name is :", course_name)
        print("teacher is :", teacher_name)
        print("place and time is :", teaching_place)
        print("---------------------------------")


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



if __name__ == "__main__":
    login(StudentID="2410xxxx", Password="xxxx")
    # cookies = load_cookies_from_file()

    selectCourse("20241-")
    getSelectedCourse()
