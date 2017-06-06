import threading
import time
from bs4 import BeautifulSoup

num = 0


class CourseThread(threading.Thread):
    def __init__(self, name, lock, content):
        threading.Thread.__init__(self)
        self.name = name
        self.lock = lock
        self.content = content

    def run(self):
        num_count = 13
        global num  # 声明为全局变量
        while num <= num_count:
            self.lock.acquire()
            local_num = num
            num += 1
            self.lock.release()
            self.show_course(local_num)
        time.sleep(0.1)

    def show_course(self, local_num):
        soup = BeautifulSoup(self.content, 'lxml')
        ticks = soup.find_all('tr', bgcolor="#FFFFFF")
        for tick in ticks:
            if tick.find('td', align="center") and tick.find('td', rowspan="13") and tick.find('td', align="center"). \
                    next_sibling.next_sibling.string.replace('\t', '').replace(' ', '').replace('\n', '') == \
                    str(local_num):
                print(tick.find('td', align="center").next_sibling.next_sibling.next_sibling.next_sibling.next_sibling
                      .next_sibling.string.replace('\t', '').replace(' ', '').replace('\n', ''), self.name)
            elif tick.find('td', align="center") and not tick.find('td', rowspan="13") and tick. \
                    find('td', align="center").string.replace('\t', '').replace('\n', '') == str(local_num):
                print(tick.find('td', align="center").next_sibling.next_sibling.next_sibling.next_sibling
                      .string.replace('\t', '').replace('\n', ''), self.name)
