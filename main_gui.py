import os
import sys

import webview

from apis import Api


def resource_path(relative_path):
    """ 获取资源绝对路径 """
    try:
        # PyInstaller创建临时文件夹，将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def create_window():
    window = webview.create_window(
        '深圳大学研究生选课助手',
        url=resource_path('index.html'),  # 直接使用index.html，不需要build路径
        js_api=Api(),
        width=1200,
        height=800,
        resizable=True,
        text_select=False,
        zoomable=False,
    )

    # 启动webview
    webview.start(debug=False)  # debug=True, 开启调试模式


if __name__ == '__main__':
    create_window()
