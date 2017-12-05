import os
import random
import tensorflow as tf
import numpy as np
from main import crack_captcha, convert2gray, char_set, crack_captcha_cnn, MAX_CAPTCHA, CHAR_SET_LEN, X, keep_prob
from PIL import Image

DIR_PATH = '../extend_datas/'
NEW_DIR_PATH = '../extend_datas_marked/'
COREECT_COUNT = 0
ERROR_COUNT = 0

def get_datas_manual():
    global COREECT_COUNT
    global ERROR_COUNT
    files = os.listdir(NEW_DIR_PATH)
    file_name = random.choice(files)
    image = Image.open(NEW_DIR_PATH + file_name)
    image.show()
    text = raw_input('predict: ' + file_name + ' ' + str(len(files)) + ' remain correct: ' + str(COREECT_COUNT) + 'error: ' + str(ERROR_COUNT) +' verifycode:\n')
    if len(text) != 0:
        if len(text) != 4:
            text = raw_input('reinput:')
        ERROR_COUNT = ERROR_COUNT + 1
        os.rename(NEW_DIR_PATH + file_name, DIR_PATH + text + '.gif')
        get_datas_manual()
    COREECT_COUNT = COREECT_COUNT + 1
    os.rename(NEW_DIR_PATH + file_name, DIR_PATH + file_name)
    get_datas_manual()


def get_datas_cnn(step):
    files = os.listdir(DIR_PATH)
    length = len(files)
    if length == 0 :
        return
    output = crack_captcha_cnn()
    saver = tf.train.Saver()
    with tf.Session() as sess:
        path = '../models/crack_capcha.model-' + str(step)
        saver.restore(sess, path)
        for i in range(length):
            files = os.listdir(DIR_PATH)
            file_name = random.choice(files)
            image = Image.open(DIR_PATH + file_name)
            image = np.array(image)
            image = convert2gray(image)
            image = image.flatten() / 255
            predict = tf.argmax(tf.reshape(output, [-1, MAX_CAPTCHA, CHAR_SET_LEN]), 2)
            text_list = sess.run(predict, feed_dict={X: [image], keep_prob: 1})
            predict_text = text_list[0].tolist()
            predict_text = map(lambda x: char_set[x], predict_text)
            os.rename(DIR_PATH + file_name, NEW_DIR_PATH + ''.join(predict_text) + '.gif')


if __name__ == '__main__':
    # get_datas_cnn(13950)
    get_datas_manual()
