# -*- coding: utf-8 -*-
# 程序入口

import setting
import time
import sys
import concurrent.futures
from functools import partial
from apis import login, selectCourse, getCourseInfo, getAllCourseInfo, getSelectedCourse

successful_courses = set()


def select_course_wrapper(course, setting):
    try:
        response = selectCourse(course["id"])
        if response is True:
            print(f"{course['name']}  {course['teacher']}  抢课成功")
            return True
        else:
            print(f"{course['name']}: {response['msg'].split(' ')[0]}")
            time.sleep(setting.delay)
            return False
    except Exception as e:
        print(f"抢课 {course['name']} 时出错: {str(e)}")
        return False


def concurrent_course_selection(course_list, setting):
    with concurrent.futures.ThreadPoolExecutor(max_workers=setting.max_workers) as executor:
        for round in range(setting.count):
            print(f"开始第 {round + 1} 轮抢课...")

            # 过滤掉已经抢到的课程
            remaining_courses = [course for course in course_list if course['id'] not in successful_courses]

            if not remaining_courses:
                print("所有课程已抢到，结束抢课")
                return True

            # 创建一个偏函数，固定 setting 参数
            select_course_partial = partial(select_course_wrapper, setting=setting)

            # 提交所有剩余课程的抢课任务
            futures = [executor.submit(select_course_partial, course) for course in remaining_courses]

            # 等待所有任务完成
            for future, course in zip(concurrent.futures.as_completed(futures), remaining_courses):
                if future.result():
                    successful_courses.add(course['id'])

            print(f"第 {round + 1} 轮抢课结束，已抢到 {len(successful_courses)} 门课程")
            if round < setting.count - 1:
                print(f"等待下一轮...")
                time.sleep(setting.delay / 1000.0)

    return len(successful_courses) == len(course_list)


if __name__ == "__main__":
    # 登录一下
    StudentID = setting.StudentID
    Password = setting.Password

    if setting.StudentID == "":
        StudentID = input("请输入学号: ")
    if setting.Password == "":
        Password = input("请输入密码: ")

    login(StudentID, Password)

    getAllCourseInfo()

    if len(setting.courses) == 0:
        while True:
            id = input("请输入你要抢的课程ID，为空则退出添加流程: ")
            if id != "":
                setting.courses.append(id)
            else:
                print("未输入课程ID，退出添加流程")
                break

    if len(setting.courses) == 0:
        print("未添加课程ID，退出抢课")
        sys.exit()
    else:
        wait = input(f"请检查选课结果，按回车键继续:\n{setting.courses}\n")

    print("抢课开始")
    course_list = []
    for course in setting.courses:
        course_info = getCourseInfo(course)
        course_list.append({"id": course, "name": course_info['KCMC'], "teacher": course_info['RKJS']})
    print(course_list)

    # 主程序
    try:
        result = concurrent_course_selection(course_list, setting)
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
        print("请检查设置 setting.py 部分是否填写正确")

    print("抢课结束")

    print("======================")
    print("您现在选课的结果如下")
    getSelectedCourse()
