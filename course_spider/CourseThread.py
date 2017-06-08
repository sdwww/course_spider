import os
import threading
import time

num = 0


class CourseThread(threading.Thread):
    def __init__(self, name, session, lock, path):
        threading.Thread.__init__(self)
        self.name = name
        self.session = session
        self.lock = lock
        self.path = path

    def run(self):
        num_count = len(self.path) - 1
        global num  # 声明为全局变量
        while num <= num_count:
            self.lock.acquire()
            local_num = num
            num += 1
            self.lock.release()
            self.download_html(local_num)
        time.sleep(0.1)

    # 保存网页内容
    def save_html(self, save_path, file_name, content):
        try:
            if not os.path.isdir(save_path + '/'):
                os.mkdir(save_path + '/')
            html = open(save_path + '/' + file_name + '.html', 'w', encoding='utf-8')
            html.write(content)
            html.close()
            return True
        except IOError:
            return False

    def download_html(self, local_num):
        try:
            if not os.path.isdir('./saved_html/' + self.path[local_num][0] + '/'):
                os.mkdir('./saved_html/' + self.path[local_num][0] + '/')
        except FileExistsError:
            pass
        html_content = self.session.get(self.path[local_num][3]).text
        if self.save_html('./saved_html/' + self.path[local_num][0] +'/'+ self.path[local_num][1],
                          self.path[local_num][2], html_content):
            print('保存网页' + self.path[local_num][2] + '成功')
        else:
            print('保存网页' + self.path[local_num][2] + '失败')
