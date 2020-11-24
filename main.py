from datetime import datetime
from sys import argv
from faker import Faker
from selenium.webdriver import ActionChains
from smsactivateru import Sms, SmsService, GetNumber, SmsTypes

from functions import *
from smspva import *


SMS_ACTIVATE = 'sms-activate'
SMS_PVA = 'smspva'


def aliexpress(driver, wait):
    # noinspection PyBroadException
    try:
        frames = driver.find_elements_by_tag_name('iframe')
        for frame in frames:
            if re.search(r'https://campaign\.aliexpress\.com', frame.get_attribute('src')):
                driver.switch_to.frame(frame)
                images = driver.find_elements_by_tag_name('img')
                for image in images:
                    if re.search(r'https://img\.alicdn\.com', image.get_attribute('src')):
                        click(image)
                        break
                driver.switch_to.default_content()
                break
        click(driver.find_element_by_class_name('user-account-port'))
        wait_element_by_class(wait, 'join-btn')
        click(driver.find_element_by_class_name('join-btn'))
        wait_element_by_class(wait, 'google')
        click(driver.find_element_by_class_name('google'))
        return driver, wait
    except Exception:
        close_browser(driver)


def google(driver, wait, sms_service=SMS_ACTIVATE, country='RU'):
    # Нажатие на кнопку Создать аккаунт для себя
    # wait_element_by_id(wait, 'ow313')
    # click(driver.find_element_by_id('ow313'))
    # pyautogui.press('down')
    # pyautogui.press('enter')

    # Ждём загрузку страницы
    wait_element_by_id(wait, 'firstName')

    # Генерируем данные
    faker = Faker()
    first_name = faker.first_name()
    last_name = faker.last_name()
    username = (first_name + last_name + str(faker.pyint()) + str(faker.pyint())).lower()
    password = faker.password()

    # Заполняем данные и переходим на следующую страницу
    logger.log('Ввожу имя')
    fill_field(driver.find_element_by_id('firstName'), first_name)
    logger.log('Ввожу фамилию')
    fill_field(driver.find_element_by_id('lastName'), last_name)
    logger.log('Ввожу никнейм')
    fill_field(driver.find_element_by_id('username'), username)
    logger.log('Ввожу пароль')
    fill_field(driver.find_element_by_name('Passwd'), password)
    logger.log('Ввожу ещё раз пароль')
    fill_field(driver.find_element_by_name('ConfirmPasswd'), password)
    click(driver.find_element_by_id('accountDetailsNext'))

    # Ждём загрузку страницы
    wait_element_by_id(wait, 'phoneNumberId')

    btn_next = driver.find_element_by_css_selector('#view_container button')

    logger.log('Ввожу номер телефона')

    count_number = 10
    index_number = 0
    skip = False
    while index_number < count_number:
        # Получаем номер телефона
        if sms_service == SMS_ACTIVATE:
            # noinspection PyBroadException
            try:
                wrapper = Sms('de4f456560f752027Ae21ce8238f4c85')
                activation = GetNumber(
                    service=SmsService().Gmail,
                    country=SmsTypes.Country().__getattribute__(country)
                ).request(wrapper)
                country_code = '+'
                number_phone = activation.phone_number
            except Exception:
                skip = True
                break
        elif sms_service == SMS_PVA:
            smspva = SmsPva()
            has_number = False
            while not has_number:
                time.sleep(70)
                response = smspva.get_number(country=country)
                if response['response'] == '5':
                    continue
                number_phone = response['number']
                phone_id = response['id']
                country_code = response['CountryCode']
                if number_phone is not None:
                    has_number = True

        # Вводим номер телефона и переходим на следующую страницу
        phone_number = driver.find_element_by_id('phoneNumberId')
        fill_field(phone_number, country_code + str(number_phone))
        # logger.log(country.lower())
        # action = ActionChains(driver)
        # action.click(driver.find_element_by_class_name('#countryList div[data-value="' + country.lower() + '"]'))
        # action.perform()
        click(btn_next)

        # noinspection PyBroadException
        try:
            while True:
                phone_number = driver.find_element_by_id('phoneNumberId')
                if phone_number.get_attribute('aria-invalid') != 'false':
                    logger.log('Деактивируем номер ' + country_code + str(number_phone))
                    if sms_service == SMS_ACTIVATE:
                        activation.mark_as_used()
                    elif sms_service == SMS_PVA:
                        smspva.denial(phone_id)
                    break
                else:
                    time.sleep(1)
        except Exception:
            logger.log('+' + number_phone)
            logger.log('Переходим дальше')
            break

        index_number += 1

        if index_number == count_number:
            skip = True
            break

    if not skip:
        # Ждём загрузку страницы
        wait_element_by_id(wait, 'code')

        logger.log('Ввожу код из СМС')

        # Получаем код из СМС
        if sms_service == SMS_ACTIVATE:
            activation.was_sent()
            try:
                code = activation.wait_code(wrapper=wrapper)
            except Exception:
                close_browser(driver)
        elif sms_service == SMS_PVA:
            response = smspva.get_sms(phone_id)
            code = response['sms']
            while code == 'null':
                response = smspva.get_sms(phone_id)
                code = response['sms']

        # Вводим код из СМС и подтверждаем
        fill_field(driver.find_element_by_id('code'), code)

        btns = driver.find_elements_by_css_selector('#view_container button')
        click(btns[1])

        # Ждём следующую страницу
        wait_element_by_id(wait, 'day')

        emails = ['4eknwerrjvjh@mail.ru', 'ewrqidacuhwe@mail.ru', 'it3zhnmvzowc@mail.ru', 'mjwfvwygjzfu@mail.ru',
                  'nueznqicdwyn@mail.ru', 'oacb4gzm4tfq@mail.ru', 'w7zictsra6pf@mail.ru']
        index = random.randint(0, len(emails) - 1)
        logger.log('Ввожу дполнительный email')
        fill_field(driver.find_element_by_css_selector('input[type="email"]'), emails[index])

        # Заполняем дату рождения и выбираем пол
        logger.log('Ввожу дату рождения и пол')
        fill_field(driver.find_element_by_id('day'), str(random.randint(1, 28)))
        click(driver.find_element_by_id('month'))

        month = random.randint(1, 12)
        i = 0
        while i < month:
            time.sleep(random.random() / 2)
            pyautogui.press('down')
            i += 1
        pyautogui.press('Enter')

        year = random.randint(20, 50)
        fill_field(driver.find_element_by_id('year'), str(datetime.now().year - year))
        click(driver.find_element_by_id('gender'))
        pyautogui.press('down')
        time.sleep(random.random())
        pyautogui.press('down')
        time.sleep(random.random())
        pyautogui.press('Enter')

        # Нажимаем на кнопку далее
        btn_next = driver.find_element_by_css_selector('#view_container button')
        click(btn_next)

        # Ждём загрузку страницы
        wait_element_by_id(wait, 'learnMore')

        # Пропускаем страницу
        btns = driver.find_elements_by_css_selector('#view_container button')
        click(btns[-1])

        # Ждём загрузку страницы
        wait_element_by_id(wait, 'termsofserviceNext')

        # Скроллим вниз страницы
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        file = open('google.txt', 'a')
        logger.log(username + '@gmail.com / ' + password)
        file.write(username + '@gmail.com / ' + password + "\r\n")
        file.close()

        # Нажимаем кнопку "Принимаю"
        logger.log('Принимаю условия')
        action = ActionChains(driver)
        checkbox = driver.find_element_by_id('selectionc0')
        action.move_to_element(checkbox)
        action.perform()
        checkbox.click()
        time.sleep(1)
        checkbox = driver.find_element_by_id('selectionc3')
        action.move_to_element(checkbox)
        action.perform()
        checkbox.click()
        time.sleep(1)
        confirm = driver.find_element_by_id('termsofserviceNext')
        action.move_to_element(confirm)
        action.perform()
        confirm.click()
        time.sleep(1)
        confirm = driver.find_element_by_id('confirmdialog-confirm')
        action.move_to_element(confirm)
        action.perform()
        confirm.click()
        return True

    return False


def main(count_account, service, country):
    index = 0
    max_attempt = count_account * 3
    current_attempt = 1
    while index < count_account and current_attempt <= max_attempt:
        logger.log('Попытка ' + str(current_attempt) + ' из ' + str(max_attempt))
        driver, wait = open_browser('https://google.com')
        # noinspection PyBroadException
        try:
            serf(driver, wait, ['https://habr.com', 'https://github.com', 'https://gitlab.com', 'https://youtube.com'])
            open_new_window(driver, 'https://google.com')
            wait_element_by_id(wait, 'searchform')
            frames = driver.find_elements_by_tag_name('iframe')
            for frame in frames:
                if re.search(r'https://consent\.google\.com', frame.get_attribute('src')):
                    driver.switch_to.frame(frame)
                    # noinspection PyBroadException
                    try:
                        click(driver.find_element_by_id('introAgreeButton'))
                    except Exception:
                        time.sleep(0)
                    driver.switch_to.default_content()
                    break
            element = driver.find_element_by_css_selector('#searchform input[name="q"]')
            fill_field(element, 'gmail')
            pyautogui.press('enter')
            wait_element_by_id(wait, 'logo')
            elements = driver.find_elements_by_tag_name('span')
            for element in elements:
                if element.text == 'Gmail - Google':
                    click(element)
                    break
            wait_element_by_class(wait, 'hero--no-carousel')
            click(driver.find_elements_by_css_selector('a[ga-event-action="create account"]')[1])
            driver.switch_to.window(driver.window_handles[-1])
            result = google(driver, wait, service, country)
            if result:
                index += 1
                logger.log('Зарегистрированно аккаунтов: ' + str(index))
            else:
                logger.log('Аккаунт не зарегистрирован')
        except Exception:
            logger.log('Не удалось зарегистрировать аккаунт')
        current_attempt += 1
        close_browser(driver)


if __name__ == '__main__':
    script_name, count_account, service, country = argv
    main(int(count_account), service, country)
