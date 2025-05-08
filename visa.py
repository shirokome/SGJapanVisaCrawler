import datetime
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import smtplib
from email.mime.text import MIMEText
from selenium.webdriver.chrome.options import Options
import re
#Configs#
#URL. Do not change it.
URL = "https://coubic.com/Embassy-of-Japan/914977/book/event_type"  
# Desired month to check, format: "YYYY年M月"               
TARGET_MONTH = "2025年5月"
# Desired dates to check, format: "YYYY年M月D日"
TARGET_DATES = [
    "2025年5月8日",
    "2025年5月9日",
    # "2025年5月20日",
]
CHECK_INTERVAL_SEC = 60                     # 检测间隔（秒）

SMTP_SERVER    = "smtp.gmail.com"
SMTP_PORT      = 587
SENDER_EMAIL   = ""
# 注意：如果你开启了 Gmail 的两步验证，下面填的是【应用专用密码】，而非你的登录密码。
SENDER_PASSWD  = ""
RECEIVER_EMAIL = SENDER_EMAIL
import sys
def make_headless_driver():
    chrome_opts = Options()
    chrome_opts.add_argument("--headless")            
    chrome_opts.add_argument("--disable-gpu")         
    chrome_opts.add_argument("--no-sandbox")          
    chrome_opts.add_argument("--disable-dev-shm-usage")  
    # 如有需要还可以设置窗口大小，方便某些响应式页面渲染：
    chrome_opts.add_argument("window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_opts)
    return driver

def send_email(subject: str, body: str):
    """发送文本邮件"""
    msg = MIMEText(body, 'plain', 'utf-8')
    msg['Subject'] = subject
    msg['From']    = SENDER_EMAIL
    msg['To']      = RECEIVER_EMAIL

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(SENDER_EMAIL, SENDER_PASSWD)
        smtp.send_message(msg)
    print("📧 已发送通知邮件")

def navigate_to_target_month(driver, target_month: str):
    """
    将日历翻页至 target_month（格式："YYYY年M月"）；
    支持向前或向后翻。
    """
    max_steps = 12  # 最多翻 12 次，防止死循环
    for _ in range(max_steps):
        lbl = driver.find_element(
            By.CSS_SELECTOR,
            ".react-calendar__navigation__label__labelText"
        ).text.strip()
        if lbl == target_month:
            print(f"✅ 已跳转到目标月份：{lbl}")
            return True

        # 解析当前年月、目标年月
        cy, cm = map(int, lbl.rstrip("月").split("年"))
        ty, tm = map(int, target_month.rstrip("月").split("年"))
        diff = (ty*12 + tm) - (cy*12 + cm)

        if diff > 0:
            # 当前月 < 目标月 ⇒ 点“下个月”
            btn = driver.find_element(
                By.CSS_SELECTOR,
                ".react-calendar__navigation__arrow.react-calendar__navigation__next-button"
            )
        else:
            # 当前月 > 目标月 ⇒ 点“上个月”
            btn = driver.find_element(
                By.CSS_SELECTOR,
                ".react-calendar__navigation__arrow.react-calendar__navigation__prev-button"
            )

        btn.click()
        time.sleep(0.5)
    print("⚠️ 翻页超过最大步数，未能跳到目标月份")
    return False
from selenium.webdriver.common.by import By

def detect_calendar_slots(driver, target_dates):
    """在日历模式下，返回哪些 target_dates 可用"""
    available = []
    tiles = driver.find_elements(By.CLASS_NAME, "react-calendar__tile")
    for d in target_dates:
        for btn in tiles:
            try:
                abbr = btn.find_element(By.TAG_NAME, "abbr")
                if abbr.get_attribute("aria-label") == d:
                    if btn.get_attribute("disabled") is None:
                        available.append(d)
                    break
            except:
                continue
    return available

def detect_time_slots_list(driver, target_dates):
    """在新版时段列表模式下，返回哪些 target_dates 有条目"""
    available = []
    # Broadly select possible slot containers
    slots = driver.find_elements(By.CSS_SELECTOR, ".flex-col")
    date_pattern = re.compile(r"^(\d{4})/(\d{2})/(\d{2})")
    for slot in slots:
        try:
            # Inspect child divs for date text
            for div in slot.find_elements(By.TAG_NAME, "div"):
                txt = div.text.strip()
                m = date_pattern.match(txt)
                if m:
                    year, month, day = m.groups()
                    # Remove leading zeros
                    norm = f"{int(year)}年{int(month)}月{int(day)}日"
                    if norm in target_dates:
                        available.append(norm)
                    break
        except:
            continue
    return sorted(set(available))
def check_and_notify():
    # driver = webdriver.Chrome()  # 或 webdriver.Firefox()
    driver = make_headless_driver()
    driver.get(URL)
    time.sleep(5)  # 等待页面、日历初次加载
    
    # 判断页面模式：日历还是列表
    calendar_present = bool(driver.find_elements(By.CLASS_NAME, "react-calendar"))
    # print(calendar_present, "calendar_present")
    if calendar_present:
        # 日历模式：打开日历，翻页，检测日历格子
        # driver.find_element(By.XPATH, "//input[@placeholder='请选择日期']").click()
        time.sleep(1)
        if not navigate_to_target_month(driver, TARGET_MONTH):
            driver.quit()
            return
        available = detect_calendar_slots(driver, TARGET_DATES)
    else:
        # 列表模式：直接检测时段列表
        available = detect_time_slots_list(driver, TARGET_DATES)

    # 合并并排序可用日期
    available = sorted(set(available))
    driver.quit()

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    statuses = []
    for d in TARGET_DATES:
        mark = "✅" if d in available else "❌"
        statuses.append(f"{mark} {d}")
    line = "; ".join(statuses)

    # 覆盖单行输出
    sys.stdout.write(f"\r{now} {line}")
    sys.stdout.flush()

    if available:
        subj = f"预约提醒：可预约日期[{', '.join(available)}]"
        body = f"检测到以下日期可预约：\n" + "\n".join(available) + f"\n\n查看页面：{URL}"
        send_email(subj, body)
        print()  # 换行，免得覆盖邮件发送日志
if __name__ == "__main__":
    while True:
        check_and_notify()
        # 随机在 50–70 秒之间睡眠
        interval = random.uniform(50, 70)
        print(f"下一次检查，{interval:.1f} 秒后开始……")
        time.sleep(interval)
