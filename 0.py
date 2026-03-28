from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options
import time
from PIL import Image
import ddddocr

# 定义用户名和密码
username = "你的学号"
password = "你的密码"
cid = ['数学建模', '探秘人体', '绘画里的中国:走进大师与经典', '英美经典名著赏析',
       '在校大学生法律风险与防范策略：经典案例分析', '中华民族发展史', '民族舞', '课程08']

# 创建 Edge 浏览器的选项对象
options = Options()
# 让浏览器在脚本执行完后不自动关闭
options.add_experimental_option("detach", True)
# 启动 Edge 浏览器
driver = webdriver.Edge(options=options)


def login01():
    # 登录页面的 URL
    login_url = "https://jwglxt.hafu.edu.cn/jwglxt/xtgl/login_slogin.html"
    # 打开登录页面
    driver.get(login_url)
    # 最大化浏览器窗口
    driver.maximize_window()
    # 滚动到页面顶部
    driver.execute_script("window.scrollTo(0,0)")

    # 等待并找到用户名输入框，输入用户名
    username_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "yhm")))
    username_input.send_keys(username)

    # 等待并找到密码输入框，输入密码
    password_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "mm")))
    password_input.send_keys(password)

    # 等待并找到验证码图片元素
    captcha_img_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "yzmPic"))
    )

    # 获取验证码图片的位置和大小
    location = captcha_img_element.location
    size = captcha_img_element.size
    left = location['x'] + 300
    right = left + size['width']
    top = location['y'] + 70
    bottom = top + size['height']
    print("Location:", location)
    print("Size:", size)
    # 保存整个页面的截图
    driver.save_screenshot('page_screenshot.png')
    # 打开页面截图
    page_image = Image.open('page_screenshot.png')
    # 裁剪出验证码图片
    captcha_image = page_image.crop((left, top, right, bottom))
    # 保存验证码图片
    captcha_image.save('captcha_images/captcha.jpg')
    print("验证码图片截取成功！")

    # 使用 ddddocr 识别验证码
    ocr = ddddocr.DdddOcr(show_ad=False, beta=True)
    # 以二进制读取验证码图片
    with open('captcha_images/captcha.jpg', 'rb') as f:
        img_bytes = f.read()
    # 识别验证码
    res = ocr.classification(img_bytes)
    print('验证码：', res)
    # 找到验证码输入框，输入识别结果
    captcha_input = driver.find_element(By.ID, "yzm")
    captcha_input.send_keys(res)
    # 找到登录按钮，点击登录
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "dl")))
    login_button.click()
    # 等待 3 秒
    time.sleep(3)


def login02():
    # 第二阶段登录的 URL
    login_url02 = 'https://jwglxt.hafu.edu.cn/jwglxt/xsxk/zzxkyzb_cxZzxkYzbIndex.html?gnmkdm=N253512&layout=default'
    try:
        # 打开第二阶段登录页面
        driver.get(login_url02)
        # 如果当前 URL 不是第二阶段登录页面，则重新登录
        while (driver.current_url != login_url02):
            login01()
            print("重新登陆了一次")
            driver.get(login_url02)
            time.sleep(1)
    except:
        print('浏览器错误或其它错误')
        time.sleep(3)


def catch_coures(ans):
    try:
        # 遍历课程列表
        for i in range(len(cid)):
            # 等待并找到搜索输入框，清空输入框，输入课程名称
            query_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="searchBox"]/div/div[1]/div/div/div/div/input')))
            query_input.clear()
            query_input.send_keys(cid[i])
            # 等待并找到查询按钮，点击查询
            query_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="searchBox"]/div/div[1]/div/div/div/div/span/button[1]')))
            query_button.click()

            # 等待并找到包含选课信息的已选课人数和选课容量的元素
            elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//font[@class='jxbrs' or @class='jxbrl']"))
            )

            # 等待页面
            time.sleep(0.5)
            arr = []

            # 存储课程已选课人数和选课容量的文本信息
            for element in elements:
                arr.append(element.text)

            # 等待并找到所有的按钮（！！！这个按钮的第一个是一个查询按钮，第二个、包括以后的才是选课按钮##########）
            all_button = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//button[@class='btn btn-primary btn-sm']"))
            )

            # 遍历所选课程的所有教学班级
            for j in range(1, len(all_button)):
                # 等待并找到选课状态元素
                status = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "/html/body/div[2]/div/div/div[6]/div/div[2]/div[1]/div[1]/h3/span[3]"))
                )
                print(str(cid[i]), str(j), "选课前状态：", status.text)
                try:
                    # 提取该课程第j个教学班级的选课人数和课程容量
                    a = int(arr[j * 2 - 2])
                    b = int(arr[j * 2 - 1])
                    print("已选课人数：", a, "    ", "课程容量人数：", b)

                    # 选课人数少于 15 人，提醒可能不开课
                    if (a < 15):
                        print("注意！！！，", str(cid[i]), "课程可能不会开课")
                    # 课程未选满且状态为未选
                    if (a < b) and '未选' in status.text:
                        print(str(cid[i]), "课程未选且没有被选满")
                        # 点击该课程第j个教学班级的选课按钮
                        catch_coures_button = all_button[j]
                        catch_coures_button.click()
                        try:
                            # 等待并查看选课的弹窗信息
                            aletr = WebDriverWait(driver, 2).until(
                                EC.presence_of_element_located(
                                    (By.XPATH, "//*[@id='alertModal']/div/div/div[2]/div/div/p"))
                            )
                            print(str(cid[i]), str(j), aletr.text)
                            # 将弹窗信息写入所选课程情况
                            ans = ans + str(cid[i]) + str(j) + aletr.text
                            # 关闭选课的弹窗信息
                            aletr_close = WebDriverWait(driver, 2).until(
                                EC.presence_of_element_located(
                                    (By.XPATH, "//*[@id='alertModal']/div/div/div[1]/button/span[1]"))
                            )
                            aletr_close.click()
                            # 继续遍历接下来的教学班级
                            continue
                        except Exception:
                            # 这是点击选课后，没有信息弹窗的情况。
                            # 查看选课操作后的课程状态
                            status = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable(
                                    (By.XPATH, "/html/body/div[2]/div/div/div[6]/div/div[2]/div[1]/div[1]/h3/span[3]"))
                            )
                            print(str(cid[i]), str(j), "选课后状态：", status.text)
                            ans = ans + str(cid[i]) + str(j) + status.text + '、'
                    else:
                        print(str(cid[i]), str(j), "课程选课前已选")
                        ans = ans + str(cid[i]) + str(j) + '课程选课前已选、'
                        # 如果该课程在点击这个教学班级选课按钮之前，就已经选上了，则无需继续遍历
                        break
                    result_cid.append(cid[i])
                except Exception:
                    print(str(cid[i]), str(j), "课程已选满")
                    ans = ans + str(cid[i]) + str(j) + '已选满、'
        return ans
    except Exception:
        print('不在选课时段或没有该课程')

    print("您已经选上的课程：", result_cid)


if __name__ == '__main__':
    # 存储已选课程的列表
    result_cid = []
    # 首次登录
    login01()
    while (1):
        # 尝试登录
        login02()
        ans = ''
        # 尝试选课
        bns = catch_coures(ans)
        print("所有课程情况：", bns)
        print('——————————————————————————————————————————')
        # 如果没有选课信息（未进入选课时间）或还有未选课程，则继续循环
        if not bns:
            time.sleep(3)
            continue
        elif '未选' in bns:
            time.sleep(3)
            continue
        else:
            # 关闭浏览器
            driver.quit()
            break


if __name__ == '__main__':
    # 存储已选课程的列表
    result_cid = []
    # 首次登录
    login01()
    while (1):
        # 尝试登录
        login02()
        ans = ''
        # 尝试选课
        bns = catch_coures(ans)
        print("所有课程情况：", bns)
        print('——————————————————————————————————————————')
        # 如果没有选课信息（未进入选课时间）或还有未选课程，则继续循环
        if not bns:
            time.sleep(3)
            continue
        elif '未选' in bns:
            time.sleep(3)
            continue
        else:
            # 关闭浏览器
            driver.quit()
            break
