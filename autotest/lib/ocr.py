# -*- coding:utf8 -*-
import os

import cv2


def get_pay_keyboard_number_location(img, pwd, module_img_path):
    """
    获取安全键盘对应的元素坐标
    :param img: 待匹配图片路径
    :param pwd: 密码字符串
    :param module_img_path: 模板图片所在目录
    :return:
    """
    numbers = set(list(pwd))
    templates = {}
    positions = {}
    for i in numbers:
        templates[i] = os.path.join(module_img_path, "n{}.png".format(i))

    img_rgb = cv2.imread(img)
    for te_num, te_path in templates.items():
        template = cv2.imread(te_path)
        w, h = template.shape[0:2]
        res = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
        # 返回truple（最小匹配度，最大匹配度，最小匹配对应坐标，最大匹配对应坐标）
        loc = cv2.minMaxLoc(res)
        if len(loc) == 4:
            positions[te_num] = loc[3]
        else:
            print("Can not found number: [{}] in image: [{}].".format(te_path, img))

    return [positions[n] for n in pwd]


if __name__ == "__main__":
    ls = get_pay_keyboard_number_location('D:\\pic\\big\\pic_data15287941779.png', '138976', "D:\\pic\\small\\1268")
    # print(ls)
