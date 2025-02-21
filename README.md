# szu_grab_course_for_yjs

基于Python的深圳大学抢课脚本(没有本科账号故只有研究生能用)。

复刻于[https://github.com/Lewin671/YourLesson](https://github.com/guiyi886/szu_grab_course.git) 和 https://github.com/guiyi886/szu_grab_course.git 后进行更新。

加入随机延时，被限制会提醒，并提供了GUI界面。


## 联系方式
邮箱：3504545011@qq.com


## 配置并运行抢课程序
0. 安装Python3(最好是Python3.7 / 3.8)
1. pip install -r requirements.txt
2. (可选) 配置`config.json`中的学号、密码(即credentials.student_id, credentials.password)
3. python3 main.py

# 使用PyInstaller打包
pyinstaller --onefile --windowed --add-data ".venv\lib\site-packages\ddddocr;ddddocr" --add-data "index.html;." main_gui.py