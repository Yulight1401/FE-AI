from PIL import Image
import urllib
import time

SAVE_PATH = '../extend_datas/'
NET_PATH = 'http://myself.hust.edu.cn:8080/selfservice/common/web/verifycode.jsp'

def get_datas_from_net(number):
    time_stamp = int(time.time())
    for i in range(0, number):
        file_name = '#' + str(i) + str(time_stamp) + '.gif'
        urllib.urlretrieve(NET_PATH, SAVE_PATH + file_name)
        # image = Image.open(SAVE_PATH + file_name)
        # image.show()


if __name__ == '__main__':
    get_datas_from_net(1000)
