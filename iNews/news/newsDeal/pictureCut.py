import cv2
import os


def image_cut(source_path, target_path):
    # 文件名
    filenames = os.listdir(source_path)
    for filename in filenames:
        # 拼接路径
        source = os.path.join(source_path, filename)
        target = os.path.join(target_path, filename)
        # 对于文件夹中所有图像
        if os.path.isfile(source):
            # 读取图像
            img = cv2.imread(source)
            # 读取宽和高
            high = img.shape[0]
            width = img.shape[1]
            # 如果是竖图
            if high > width:
                # 将高度拉伸至宽度为1460时的对应像素
                high_scale = int(high * (1460 / width))
                if high_scale < 1000:
                    high_scale = 1000
                img = cv2.resize(img, (high_scale, 1000))
            # 如果是横图
            else:
                # 将宽度拉伸至高度为1000时的对应像素
                width_scale = int(width * (1000 / high))
                if width_scale < 1460:
                    width_scale = 1460
                img = cv2.resize(img, (width_scale, 1000))
            # 拉伸后的宽和高
            high_s = img.shape[0]
            width_s = img.shape[1]
            # 从中心开始截取1460*1000像素
            a = int(high_s / 2 - 500)
            b = int(high_s / 2 + 500)
            c = int(width_s / 2 - 730)
            d = int(width_s / 2 + 730)
            img_cut = img[a:b, c:d]
            # 保存目标路径下
            cv2.imwrite(target, img_cut)
            os.remove(source)


def picture_deal():
    # 源路径
    source_path = '/home/bxp/Downloads/news_images'
    # 目标路径
    target_path = '/home/bxp/PycharmProjects/iNews/media/image'
    image_cut(source_path, target_path)
