import tensorflow as tf
import cv2
import numpy as np
import symclass
CLASS_NUM = len(symclass.sym_classes)
def classify_img(imgset):
    # x = tf.placeholder("float", [None, 784])
    x = tf.placeholder(tf.float32, [None, 784])

    # y_ = tf.placeholder("float", [None,10])
    y_ = tf.placeholder(tf.float32, [None, CLASS_NUM])

    # cross_entropy = -tf.reduce_sum(y_*tf.log(y))
    sess = tf.InteractiveSession()

    def weight_variable(shape):
        initial = tf.truncated_normal(shape, stddev=0.1)
        return tf.Variable(initial)

    def bias_variable(shape):
        initial = tf.constant(0.1,shape=shape)
        return tf.Variable(initial)

    def conv2d(x,W):
        return tf.nn.conv2d(x,W,strides=[1,1,1,1],padding="SAME")

    def max_pool_2x2(x):
        return tf.nn.max_pool(x, ksize=[1,2,2,1],strides=[1,2,2,1],padding="SAME")

    W_conv1 = weight_variable([5,5,1,32]);
    b_conv1 = bias_variable([32])

    x_image = tf.reshape(x, [-1,28,28,1])

    h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
    h_pool1 = max_pool_2x2(h_conv1)

    W_conv2 = weight_variable([5,5,32,32])
    b_conv2 = bias_variable([32])

    h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
    h_pool2 = max_pool_2x2(h_conv2)

    W_fc1 = weight_variable([7*7*32, 512])
    b_fc1 = bias_variable([512])

    h_pool2_flat = tf.reshape(h_pool2, [-1, 7*7*32])
    h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1)+b_fc1)
    keep_prob = tf.placeholder("float")
    h_fc1_drop = tf.nn.dropout(h_fc1,keep_prob)
    W_fc2 = weight_variable([512,CLASS_NUM])
    b_fc2 = bias_variable([CLASS_NUM])
    y_conv = tf.nn.softmax(tf.matmul(h_fc1_drop,W_fc2)+b_fc2)

    cross_entropy = -tf.reduce_sum(y_*tf.log(y_conv))
    train_step = tf.train.AdamOptimizer(3*1e-6).minimize(cross_entropy)
    correct_prediction = tf.equal(tf.argmax(y_conv,1), tf.argmax(y_,1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))
    saver = tf.train.Saver()
    inputset = []
    for img in imgset:
        img = cv2.resize(img,(28,28))
        img = img.reshape(28 * 28)
        tmp = []
        for i in range(784):
            tmp.append(1.0 - float(img[i]) / 255.0)
        inputset.append(np.array(tmp))


    print inputset[0].shape
    print len(inputset)
    saver.restore(sess,'./test_model-54901')
    a = y_conv.eval(feed_dict={x:inputset,keep_prob:1.0})
    tf.reset_default_graph()
    classList = []
    for i in range(len(a)):
        classList.append(symclass.sym_classes[np.argmax(a[i])])
    return classList
