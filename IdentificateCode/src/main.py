# -*- coding: utf-8 -*-
from  captcha.image import ImageCaptcha
import numpy as  np
import os
import matplotlib.pyplot as  plt
from  PIL import Image, ImageFont, ImageDraw
import random
import re
import tensorflow as tf

number = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
            'v', 'w', 'x', 'y', 'z']
Alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
            'V', 'W', 'X', 'Y', 'Z']

gene_char_set = number + alphabet + Alphabet
char_set = number + alphabet

# 1为全部选择爬取的数据
MUTI_VALUE = 0.20
TEST_DATA_PATH = '../datas/'
##图片高40 60
IMAGE_HEIGHT = 40
##图片宽75 160
IMAGE_WIDTH = 75
##验证码长度
MAX_CAPTCHA = 4
##验证码选择空间
CHAR_SET_LEN = len(char_set)
##提前定义变量空间
X = tf.placeholder(tf.float32, [None, IMAGE_HEIGHT * IMAGE_WIDTH])
Y = tf.placeholder(tf.float32, [None, MAX_CAPTCHA * CHAR_SET_LEN])
keep_prob = tf.placeholder(tf.float32)  ##节点保留率


##生成n位验证码字符 这里n=4
def random_text(char_set=gene_char_set, captcha_size=4):
    captcha_text = []
    for i in range(captcha_size):
        c = random.choice(char_set)
        captcha_text.append(c)
    return captcha_text

##混合爬取与随机生成的数据
def get_multi_datas():
    random_choice = random.random()
    if random_choice < MUTI_VALUE:
        captcha_text, captcha_image = get_test_image()
    else:
        captcha_text, captcha_image = gene_image_text()
    return captcha_text, captcha_image

##使用ImageCaptcha库生成验证码
def gene_image_text():
    #自己的生成算法
    image = Image.new('RGB', (IMAGE_WIDTH, IMAGE_HEIGHT), (255, 255, 255, 255))
    font = ImageFont.truetype('../font/xiuyin5-Bold.otf', 28)
    draw = ImageDraw.Draw(image)
    # captcha_text = ['7', 'u', 'e', 'f']
    captcha_text = random_text()
    shink_size = 6 + (random.random() * 6 - 3)
    random_size = 0.4
    offset = (random.random() * 14 - 7) + 6
    for index in range(4):
        text = captcha_text[index]
        font_width, font_height = font.getsize(text)
        random_offset = random.random() * random_size - random_size / 2
        draw.text((index * (IMAGE_WIDTH - font_width * random_offset) / MAX_CAPTCHA + shink_size * (MAX_CAPTCHA / 2 - index) - offset, (IMAGE_HEIGHT - font_height + 11) / MAX_CAPTCHA), text,
                font= font,fill=(245, 208, 0, 255))

    # print(captcha_text)
    # image.show()
    captcha_image = image
    captcha_image = np.array(captcha_image)

    # #captcha生成
    # image = ImageCaptcha()
    # captcha_text = random_text()
    # captcha_text = ''.join(captcha_text)
    # captcha = image.generate(captcha_text)
    # captcha_image = Image.open(captcha)
    # captcha_image = np.array(captcha_image)

    # #直接使用训练集
    # captcha_text, captcha_image = get_test_image()
    return map(lambda x: x.lower(), captcha_text), captcha_image


##彩色图转化为灰度图
def convert2gray(img):
    if len(img.shape) > 2:
        gray = np.mean(img, -1)
        # 上面的转法较快，正规转法如下
        # r, g, b = img[:,:,0], img[:,:,1], img[:,:,2]
        # gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
        return gray
    else:
        return img


##获取字符在 字符域中下标
def getPos(char_set=char_set, char=None):
    return char_set.index(char)


##验证码字符转换为长向量
def text2vec(text):
    text_len = len(text)
    if text_len > MAX_CAPTCHA:
        raise ValueError('验证码最长4个字符')

    vector = np.zeros(MAX_CAPTCHA * CHAR_SET_LEN)
    """
    def char2pos(c):
        if c =='_':
            k = 62
            return k
        k = ord(c)-48
        if k > 9:
            k = ord(c) - 55
            if k > 35:
                k = ord(c) - 61
                if k > 61:
                    raise ValueError('No Map')
        return k
    """
    for i, c in enumerate(text):
        idx = i * CHAR_SET_LEN + getPos(char=c)
        vector[idx] = 1
    return vector


##获得1组验证码数据
def get_next_batch(batch_size=128):
    batch_x = np.zeros([batch_size, IMAGE_HEIGHT * IMAGE_WIDTH])
    batch_y = np.zeros([batch_size, MAX_CAPTCHA * CHAR_SET_LEN])

    def wrap_gene_image_text():
        while 1:
            text, image = get_multi_datas()
            if image.shape == (IMAGE_HEIGHT, IMAGE_WIDTH, 3):
                return text, image

    for i in range(batch_size):
        text, image = wrap_gene_image_text()
        image = convert2gray(image)
        batch_x[i, :] = image.flatten() / 255
        batch_y[i, :] = text2vec(text)
    return batch_x, batch_y


##卷积层 附relu  max_pool drop操作
def conn_layer(w_alpha=0.01, b_alpha=0.1, _keep_prob=0.7, input=None, last_size=None, cur_size=None):
    w_c1 = tf.Variable(w_alpha * tf.random_normal([3, 3, last_size, cur_size]))
    b_c1 = tf.Variable(b_alpha * tf.random_normal([cur_size]))
    conv1 = tf.nn.relu(tf.nn.bias_add(tf.nn.conv2d(input, w_c1, strides=[1, 1, 1, 1], padding='SAME'), b_c1))
    conv1 = tf.nn.max_pool(conv1, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
    conv1 = tf.nn.dropout(conv1, keep_prob=_keep_prob)
    return conv1


##对卷积层到全链接层的数据进行变换
def _get_conn_last_size(input):
    shape = input.get_shape().as_list()
    dim = 1
    for d in shape[1:]:
        dim *= d
    input = tf.reshape(input, [-1, dim])
    return input, dim


##全链接层
def _fc_layer(w_alpha=0.01, b_alpha=0.1, input=None, last_size=None, cur_size=None):
    w_d = tf.Variable(w_alpha * tf.random_normal([last_size, cur_size]))
    b_d = tf.Variable(b_alpha * tf.random_normal([cur_size]))
    fc = tf.nn.bias_add(tf.matmul(input, w_d), b_d)
    return fc


##构建前向传播网络
def crack_captcha_cnn(w_alpha=0.01, b_alpha=0.1):
    x = tf.reshape(X, shape=[-1, IMAGE_HEIGHT, IMAGE_WIDTH, 1])

    conv1 = conn_layer(input=x, last_size=1, cur_size=32)
    conv2 = conn_layer(input=conv1, last_size=32, cur_size=64)
    conn3 = conn_layer(input=conv2, last_size=64, cur_size=64)

    input, dim = _get_conn_last_size(conn3)

    fc_layer1 = _fc_layer(input=input, last_size=dim, cur_size=1024)
    fc_layer1 = tf.nn.relu(fc_layer1)
    fc_layer1 = tf.nn.dropout(fc_layer1, keep_prob)

    fc_out = _fc_layer(input=fc_layer1, last_size=1024, cur_size=MAX_CAPTCHA * CHAR_SET_LEN)
    return fc_out


##反向传播
def back_propagation():
    output = crack_captcha_cnn()
    ##学习率
    loss = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(output, Y))
    optm = tf.train.AdamOptimizer(learning_rate=0.001).minimize(loss)
    predict = tf.reshape(output, [-1, MAX_CAPTCHA, CHAR_SET_LEN])
    max_idx_p = tf.arg_max(predict, 2)
    max_idx_l = tf.arg_max(tf.reshape(Y, [-1, MAX_CAPTCHA, CHAR_SET_LEN]), 2)
    accuracy = tf.reduce_mean(tf.cast(tf.equal(max_idx_p, max_idx_l), tf.float32))
    return loss, optm, accuracy


##初次运行训练模型
def train_first():
    loss, optm, accuracy = back_propagation()

    saver = tf.train.Saver()
    with tf.Session() as  sess:
        sess.run(tf.global_variables_initializer())
        step = 0
        while 1:
            batch_x, batch_y = get_next_batch(20)
            _, loss_ = sess.run([optm, loss], feed_dict={X: batch_x, Y: batch_y, keep_prob: 0.75})
            if step % 50 == 0:
                batch_x_test, batch_y_test = get_next_batch(100)
                acc = sess.run(accuracy, feed_dict={X: batch_x_test, Y: batch_y_test, keep_prob: 1.})
                print(step, acc, loss_)
                if acc > 0.80:
                    saver.save(sess, '../models/crack_capcha.model', global_step=step)
                    break
            step += 1


##加载现有模型 继续进行训练
def train_continue(step):
    loss, optm, accuracy = back_propagation()

    saver = tf.train.Saver()
    with tf.Session() as sess:
        path = "../models/crack_capcha.model-" + str(step)
        saver.restore(sess, path)
        ##36300 36300 0.9325 0.0147698
        while 1:
            batch_x, batch_y = get_next_batch(200)
            _, loss_ = sess.run([optm, loss], feed_dict={X: batch_x, Y: batch_y, keep_prob: 0.75})
            if step % 50 == 0:
                batch_x_test, batch_y_test = get_next_batch(200)
                acc = sess.run(accuracy, feed_dict={X: batch_x_test, Y: batch_y_test, keep_prob: 1.})
                print(step, acc, loss_)
                if acc >= 0.945:
                    saver.save(sess, '../models/crack_capcha.model', global_step=step)
                    break
                # if acc >= 0.85:
                #     saver.save(sess, '../models/crack_capcha.model', global_step=step)
                #     step += 1
                #     continue
                # if acc >= 0.80:
                #     saver.save(sess, '../models/crack_capcha.model', global_step=step)
            step += 1


##测试训练模型
def crack_captcha(captcha_image, step):
    output = crack_captcha_cnn()

    saver = tf.train.Saver()
    with tf.Session() as sess:
        path = '../models/crack_capcha.model-' + str(step)
        saver.restore(sess, path)

        predict = tf.argmax(tf.reshape(output, [-1, MAX_CAPTCHA, CHAR_SET_LEN]), 2)
        text_list = sess.run(predict, feed_dict={X: [captcha_image], keep_prob: 1})
        text = text_list[0].tolist()
        return text

def get_test_image():
    files = os.listdir(TEST_DATA_PATH)
    file_name = random.choice(files)
    text = list(file_name.split('.')[0].lower())
    if len(text) != 4:
        file_name = files[0]
        text = list(file_name.split('.')[0])
    image = Image.open(TEST_DATA_PATH + file_name)
    image = image.resize((IMAGE_WIDTH, IMAGE_HEIGHT), Image.ANTIALIAS)
    image = np.array(image)
    return text, image

def get_test_image_more(name):
    text = list(name.split('.')[0].lower())
    image = Image.open('../test_datas/' + name)
    image = image.resize((IMAGE_WIDTH, IMAGE_HEIGHT), Image.ANTIALIAS)
    image = np.array(image)
    return text, image

if __name__ == '__main__':
    # gene_image_text()
    train = 1
    if train:
        train_continue(13950)
        # train_first()
    else:
        # text, image = get_multi_datas()
        # text, image = get_test_image()
        # text, image1 = gene_image_text()
        text, image = get_test_image_more('LwnT.gif')

        f = plt.figure()
        ax = f.add_subplot(111)
        ax.text(0.2, 0.9, ['right:'] + text, ha='center', va='center', transform=ax.transAxes)

        image2 = convert2gray(image)
        image2 = image2.flatten() / 255

        predict_text = crack_captcha(image2, 13950)
        print("正确: {}  预测: {}".format(text, [char_set[char] for i, char in enumerate(predict_text)]))

        ax = f.add_subplot(111)
        ax.text(0.6, 0.9, ['predict: '] + [char_set[char] for i, char in enumerate(predict_text)], ha='center', va='center', transform=ax.transAxes)

        # plt.imshow(image1)
        # plt.show()
        plt.imshow(image)
        plt.show()
