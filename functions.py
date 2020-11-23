import re
import time
import zipfile

import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import visibility_of_element_located
from selenium.webdriver.support.wait import WebDriverWait
from line_noise import *
from telegram_logger import TelegramLogger


logger = TelegramLogger('1408203026:AAHe4MWu0SCgXoP3B9ERN3FwpgLYnz5FJRo', '390734922')


def open_browser(url, port=7000, host='gate.smartproxy.com'):
    logger.log('Открываем браузер')

    PROXY_HOST = host
    PROXY_PORT = port
    PROXY_USER = 'fbworker'
    PROXY_PASS = 'fbworker'

    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = """
    var config = {
            mode: "fixed_servers",
            rules: {
              singleProxy: {
                scheme: "http",
                host: "%s",
                port: parseInt(%s)
              },
              bypassList: ["localhost"]
            }
          };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    """ % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)

    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    pluginfile = 'proxy_auth_plugin.zip'
    with zipfile.ZipFile(pluginfile, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)
    options.add_extension(pluginfile)

    driver = webdriver.Chrome(
        executable_path="/usr/local/bin/chromedriver",
        options=options
    )
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'
    })
    pyautogui.press('F11')
    screen_width, screen_height = pyautogui.size()
    move_cursor_to(screen_width / 2, screen_height / 2)
    wait = WebDriverWait(driver, 120)
    driver.get(url)
    return driver, wait


def close_browser(driver):
    logger.log('Закрываем браузер')
    driver.quit()


def open_new_window(driver, url):
    pyautogui.keyDown('ctrl')
    pyautogui.keyDown('t')
    pyautogui.keyUp('t')
    pyautogui.keyUp('ctrl')
    pyautogui.press('f11')
    pyautogui.press('f6')
    write(url)
    pyautogui.press('enter')
    pyautogui.press('f11')
    driver.switch_to.window(driver.window_handles[-1])


def wait_element_by_id(wait, element_id):
    wait.until(visibility_of_element_located((By.ID, element_id)))
    time.sleep(1)


def wait_element_by_class(wait, element_class):
    wait.until(visibility_of_element_located((By.CLASS_NAME, element_class)))
    time.sleep(1)


def page_has_loaded(driver):
    page_state = driver.execute_script('return document.readyState;')
    return page_state == 'complete'


def wait_for_ajax(wait, driver):
    # noinspection PyBroadException
    try:
        wait.until(driver.execute_script('return jQuery.active') == 0)
        logger.log('Активных ajax запросов нет')
        wait.until(driver.execute_script('return document.readyState') == 'complete')
        logger.log('Страница полностью загружена')
    except Exception:
        pass


def move_cursor_to(x, y):
    t0 = time.time()
    mouse_x, mouse_y = pyautogui.position()
    points = get_noised_line(mouse_x, mouse_y, int(x), int(y))
    duration = 1
    index = 0
    while index < len(points) - 1:
        elapsed = time.time() - t0
        index = min(int(elapsed / duration * (len(points) - 1)), len(points) - 1)
        pyautogui.moveTo(points[index][0], points[index][1])
    pyautogui.moveTo(points[-1][0], points[-1][1])


def get_coords(elem):
    # noinspection PyBroadException
    try:
        offset_x = elem.size['width'] if int(elem.size['width']) <= 5 else random.randint(5, int(elem.size['width']) - 5)
        offset_y = elem.size['height'] if int(elem.size['height']) <= 5 else random.randint(5, int(elem.size['height']) - 5)
        return elem.location['x'] + offset_x, elem.location['y'] + offset_y
    except Exception:
        return elem.location['x'] + 1, elem.location['y'] + 1


def write(text, typo=False):
    for char in text:
        time.sleep(random.random() / 2)
        if random.randint(0, 10) == 0 and typo and re.search(r'[a-z]', char) is not None:
            count = random.randint(1, 3)
            i = 0
            while i < count:
                rand = random.randint(0, len(text) - 1)
                while re.search(r'[a-z]', text[rand]) is None:
                    rand = random.randint(0, len(text) - 1)
                time.sleep(random.random() / 2)
                pyautogui.write(text[rand])
                i += 1
            i = 0
            while i < count:
                time.sleep(random.random() / 2)
                pyautogui.press('backspace')
                i += 1
            time.sleep(random.random() / 2)
            pyautogui.write(char)
        else:
            pyautogui.write(char)


def fill_field(elem, text=None):
    click(elem)
    if text is not None:
        if elem.get_attribute('value') != '':
            count = len(elem.get_attribute('value'))
            while count:
                pyautogui.press('right')
                pyautogui.press('backspace')
                count = len(elem.get_attribute('value'))
        write(text, True)


def click(elem):
    elem_x, elem_y = get_coords(elem)
    move_cursor_to(elem_x, elem_y)
    pyautogui.click()


def serf(driver, wait, urls):
    random.shuffle(urls)
    # count_url = int((len(urls) / 4) + 1)
    # urls = urls[0:count_url]
    screen_width, screen_height = pyautogui.size()
    for url in urls:
        logger.log('URL: ' + url)
        open_new_window(driver, url)
        wait_for_ajax(wait, driver)
        time.sleep(10)
        count = random.randint(3, 10)
        logger.log('Количество переходов: ' + str(count))
        index = 0
        while index < count:
            logger.log('Индекс: ' + str(index))
            links = driver.find_elements_by_tag_name('a')
            logger.log('Количество ссылок: ' + str(len(links)))
            if len(links) == 0:
                break
            else:
                current_link = links[random.randint(0, (len(links) - 1))]
                current_link_x, current_link_y = get_coords(current_link)
                while current_link_x >= screen_width or current_link_y >= screen_height \
                        or current_link_x <= 10 or current_link_y <= 10:
                    current_link = links[random.randint(0, (len(links) - 1))]
                    current_link_x, current_link_y = get_coords(current_link)
                logger.log(current_link.get_attribute('href'))
                logger.log(str(current_link_x) + ', ' + str(current_link_y))
                driver.execute_script("window.scrollTo(0, 0);")
                click(current_link)
                driver.switch_to.window(driver.window_handles[-1])
                index += 1
                wait_for_ajax(wait, driver)
                delay = random.randint(3, 10)
                logger.log('Задержка ' + str(delay) + ' сек.')
                time.sleep(delay)
