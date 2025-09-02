# -*- coding: utf-8 -*-
# 程序入口

import sys
import time

from apis import login, getCourseInfo, getAllCourseInfo, getSelectedCourse, concurrent_course_selection, \
    successful_courses, Api

if __name__ == "__main__":
    api = Api()
    config = api.load_config()

    # 初始化课程列表
    courses = []

    # 登录
    StudentID = config.get("credentials", {}).get("student_id", "")
    Password = config.get("credentials", {}).get("password", "")
    if StudentID == "":
        StudentID = input("请输入学号: ")
    if Password == "":
        Password = input("请输入密码: ")

    # 登录请求限制检查
    can_request, message = api.check_rate_limits()
    if not can_request:
        print(f"错误: {message}")
        sys.exit()

    if login(StudentID, Password):
        api.record_request()
    else:
        print("登录失败")
        sys.exit()

    # 获取可选课程信息的请求限制检查
    can_request, message = api.check_rate_limits()
    if not can_request:
        print(f"错误: {message}")
        sys.exit()

    getAllCourseInfo()
    api.record_request()

    if len(courses) == 0:
        while True:
            id = input("请输入你要抢的课程ID，为空则退出添加流程: ")
            if id != "":
                courses.append(id)
            else:
                print("未输入课程ID，退出添加流程")
                break

    if len(courses) == 0:
        print("未添加课程ID，退出抢课")
        sys.exit()
    else:
        wait = input(f"请检查选课结果，按回车键继续:\n{courses}\n")

    print("抢课开始")
    course_list = []
    for course in courses:
        # 获取课程信息的请求限制检查
        can_request, message = api.check_rate_limits()
        if not can_request:
            print(f"错误: {message}")
            time.sleep(5)  # 等待5秒后继续
            can_request, message = api.check_rate_limits()
            if not can_request:
                print("请求频率仍然过高，程序退出")
                sys.exit()

        course_info = getCourseInfo(course)
        api.record_request()
        course_list.append({"id": course, "name": course_info['KCMC'], "teacher": course_info['RKJS']})
    print(course_list)

    # 主程序
    try:
        # 从配置文件获取设置
        config_setting = config.get("settings", {
            "delay": 2,
            "max_workers": 4,
            "count": 100
        })

        result = concurrent_course_selection(course_list, config_setting, lambda: False)
        if result:
            print("所有课程抢课成功")
        else:
            print(
                f"抢课结束，成功抢到 {len(successful_courses)} 门课程，还有 {len(course_list) - len(successful_courses)} 门课程未抢到")
    except KeyboardInterrupt:
        print("通过键盘中断退出程序")
        sys.exit()
    except Exception as e:
        print(f"出现错误: {str(e)}")
        print("请检查设置 config.json 部分是否填写正确")

    print("抢课结束")

    print("======================")
    print("您现在选课的结果如下")

    # 获取选课结果的请求限制检查
    can_request, message = api.check_rate_limits()
    if not can_request:
        print(f"错误: {message}")
        time.sleep(5)
        can_request, message = api.check_rate_limits()
        if not can_request:
            print("无法获取选课结果，请稍后手动查看")
            sys.exit()

    getSelectedCourse()
    api.record_request()
