import requests
from bs4 import BeautifulSoup
import time
import os


def save_image(session, image_url, image_dir, image_name):
    response = session.get(image_url, stream=True)
    image = response.content
    with open(image_dir + '/' + image_name + '.jpg', "wb") as jpg:
        jpg.write(image)
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


if __name__ == "__main__":
    start = time.clock()
    session = requests.session()

    # 获取验证码
    login_validate = 'http://gradms.sdu.edu.cn/validatecode.jpg'
    save_image(session, login_validate, './saved_jpg', 'validate_code')

    # 输入用户名，密码，验证码进行登录
    validate_code = input("请输入验证码：")
    login_post_data = {'login_strLoginName': '*****', 'login_strPassword': '******',
                       'login_strVerify': validate_code, 'login_autoLoginCheckbox': '1'}
    login_url = 'http://gradms.sdu.edu.cn/bsuims/bsMainFrameInit.do'
    session.post(url=login_url, data=login_post_data)

    # 获取课程网页并保存
    course_content = session.get('http://gradms.sdu.edu.cn/cultivate/cultivate_selectCourseShow.do').text
    if save_html('./saved_htmls', 'course', course_content):
        print('saved finished')
    else:
        print('saved failed')

    # 解析课程名
    soup = BeautifulSoup(course_content, 'lxml')
    ticks = soup.find_all('tr', bgcolor="#FFFFFF")
    for tick in ticks:
        if tick.find('td', align="center") and tick.find('td', rowspan="13"):
            print(tick.find('td', align="center").next_sibling.next_sibling.next_sibling.next_sibling
                  .next_sibling.next_sibling.string.replace('\t', '').replace(' ', '').replace('\n', ''))
        elif tick.find('td', align="center") and not tick.find('td', rowspan="13"):
            print(tick.find('td', align="center").next_sibling.next_sibling.next_sibling.next_sibling
                  .string.replace('\t', '').replace('\n', ''))

    print('总时间为:', time.clock() - start)
