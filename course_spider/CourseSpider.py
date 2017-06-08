import os
import threading
import time
from http import cookiejar

import requests
from PIL import Image
from bs4 import BeautifulSoup

from CourseThread import CourseThread


# 判断用户是否已经登录
def is_login(session, header):
    url = "http://gradms.sdu.edu.cn/person/stuinfo_studentAllInfo.do"
    login_code = session.get(url, headers=header, allow_redirects=False).status_code
    if login_code == 200:
        return True
    else:
        return False


# 输入用户名，密码，验证码进行登录
def login(session, header):
    name = input("请输入用户名：")
    password = input("请输入密码：")
    print("请输入验证码：", end='')
    # 获取验证码
    save_image(session, './saved_jpg', 'validate_code')
    validate_code = input()
    login_post_data = {'login_strLoginName': name, 'login_strPassword': password,
                       'login_strVerify': validate_code, 'login_autoLoginCheckbox': '1'}
    login_url = 'http://gradms.sdu.edu.cn/bsuims/bsMainFrameInit.do'
    session.post(url=login_url, data=login_post_data, headers=header)
    session.cookies.save(ignore_discard=True, ignore_expires=True)


# 保存验证码并打开
def save_image(session, image_dir, image_name):
    image_url = 'http://gradms.sdu.edu.cn/validatecode.jpg'
    response = session.get(image_url, stream=True)
    image = response.content
    if not os.path.isdir(image_dir + '/'):
        os.mkdir(image_dir + '/')
    with open(image_dir + '/' + image_name + '.jpg', "wb") as jpg:
        jpg.write(image)
    try:
        im = Image.open(image_dir + '/' + image_name + '.jpg')
        im.show()
        im.close()
    except IOError:
        print('请手动打开' + image_dir + '下的验证码')
    return True


# 保存网页内容
def save_html(save_path, file_name, content):
    try:
        if not os.path.isdir(save_path + '/'):
            os.mkdir(save_path + '/')
        html = open(save_path + '/' + file_name + '.html', 'w', encoding='utf-8')
        html.write(content)
        html.close()
        return True
    except IOError:
        return False


def get_left_menu(session):
    # 获取课程网页并保存
    content = session.get('http://gradms.sdu.edu.cn/bsuims/bsMainFrameLeftMenuReload.do?'
                          'contextName=bsUimsLeftMenuPage&currentMenuName=104').text
    if save_html('./saved_html', 'left_menu', content):
        print('网页保存成功')
    else:
        print('网页保存失败')
    return content

#解析网页
def parser_html(content):
    soup = BeautifulSoup(content, 'lxml')
    # print(soup.prettify())
    ticks = soup.find('td').find_all('a')
    top_path = ''
    middle_path = ''
    complete_path = []
    for tick in ticks:
        if tick.string:
            complete_path.append([top_path, middle_path, tick.string, 'http://gradms.sdu.edu.cn' + tick.get('href')])
        elif tick.find('img').get('id') == 'treeimg1':
            top_path = tick.next_sibling
        else:
            middle_path = tick.next_sibling
    return complete_path


# 创建多线程
def create_threads(thread_count, session, lock, path):
    threads = []
    for i in range(thread_count):
        course_thread = CourseThread(name=i, session=session,lock=lock, path=path)
        course_thread.start()
        threads.append(course_thread)
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    start = time.clock()
    course_session = requests.session()
    course_session.cookies = cookiejar.LWPCookieJar(filename='course_cookies')
    try:
        course_session.cookies.load(ignore_discard=True)
    except IOError:
        print("Cookie 未能加载")

    # 构造headers
    agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' \
            '(KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36'
    headers = {
        "Host": "gradms.sdu.edu.cn",
        'User-Agent': agent
    }

    if not is_login(course_session, header=headers):
        login(session=course_session, header=headers)
    else:
        pass

    left_content = get_left_menu(course_session)
    complete_path = parser_html(left_content)

    course_lock = threading.RLock()
    create_threads(thread_count=3, session=course_session, lock=course_lock, path=complete_path)
    print('总时间为:', time.clock() - start)
