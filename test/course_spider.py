import requests
from bs4 import BeautifulSoup
from PIL import Image
import time
import os

try:
    import cookielib
except:
    import http.cookiejar as cookielib


def is_login(session, headers):
    url = "http://gradms.sdu.edu.cn/person/stuinfo_studentAllInfo.do"
    login_code = session.get(url, headers=headers, allow_redirects=False).status_code
    if login_code == 200:
        return True
    else:
        return False


def login(session, headers):
    name = input("请输入用户名：")
    password = input("请输入密码：")
    # 获取验证码
    save_image(session, './saved_jpg', 'validate_code')
    validate_code = input("请输入验证码：")
    login_post_data = {'login_strLoginName': name, 'login_strPassword': password,
                       'login_strVerify': validate_code, 'login_autoLoginCheckbox': '1'}
    login_url = 'http://gradms.sdu.edu.cn/bsuims/bsMainFrameInit.do'
    session.post(url=login_url, data=login_post_data, headers=headers)
    session.cookies.save(ignore_discard=True, ignore_expires=True)


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
    except:
        print('请手动打开' + image_dir + '下的验证码')
    return True


def save_html(save_path, file_name, content):
    try:
        if not os.path.isdir(save_path + '/'):
            os.mkdir(save_path + '/')
        html = open(save_path + '/' + file_name + '.html', 'w', encoding='utf-8')
        html.write(content)
        html.close()
        return True
    except:
        return False


def parser_html(course_content):
    soup = BeautifulSoup(course_content, 'lxml')
    ticks = soup.find_all('tr', bgcolor="#FFFFFF")
    for tick in ticks:
        if tick.find('td', align="center") and tick.find('td', rowspan="13"):
            print(tick.find('td', align="center").next_sibling.next_sibling.next_sibling.next_sibling
                  .next_sibling.next_sibling.string.replace('\t', '').replace(' ', '').replace('\n', ''))
        elif tick.find('td', align="center") and not tick.find('td', rowspan="13"):
            print(tick.find('td', align="center").next_sibling.next_sibling.next_sibling.next_sibling
                  .string.replace('\t', '').replace('\n', ''))


if __name__ == "__main__":
    start = time.clock()
    session = requests.session()
    session.cookies = cookielib.LWPCookieJar(filename='course_cookies')
    try:
        session.cookies.load(ignore_discard=True)
    except:
        print("Cookie 未能加载")

    # 构造headers
    agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' \
            '(KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36'
    headers = {
        "Host": "gradms.sdu.edu.cn",
        'User-Agent': agent
    }
    if not is_login(session, headers):

        # 输入用户名，密码，验证码进行登录
        login(session=session, headers=headers)
    else:
        pass
    # 获取课程网页并保存
    course_content = session.get('http://gradms.sdu.edu.cn/cultivate/cultivate_selectCourseShow.do').text
    if save_html('./saved_htmls', 'course', course_content):
        print('saved finished')
    else:
        print('saved failed')

    # 解析课程名
    parser_html(course_content)

    print('总时间为:', time.clock() - start)
