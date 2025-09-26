import pytest
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains


def test_login_empty_username(browser):
    '''TC-001: Вход с пустым логином'''
    password_input = WebDriverWait(browser, 3).until(EC.presence_of_element_located((By.ID, 'password')))
    password_input.send_keys('TestPassword123')

    login_button = browser.find_element(By.ID, 'kc-login')
    login_button.click()

    current_url = browser.current_url
    login_form = browser.find_element(By.CLASS_NAME, 'login-form-container')

    login_button = browser.find_element(By.ID, 'kc-login')
    login_button.click()
    try:
        error = WebDriverWait(browser, 3).until(EC.presence_of_element_located((By.ID, 'username-meta')))
        assert 'Введите логин' in error.text, 'Не было выведено надписи "Введите логин"'
    except Exception:
        raise AssertionError('Не появилось сообщение "Введите логин" при пустом поле логина')

    try:
        WebDriverWait(browser, 2).until(
            lambda driver: driver.current_url != current_url
                           or EC.staleness_of(login_form)(driver)
        )
        raise AssertionError('Кнопка должна быть заблокирована: страница не должна перезагружаться')
    except TimeoutException:
        pass


def test_login_empty_password(browser):
    '''TC-002: Вход с пустым паролем'''
    username_input = WebDriverWait(browser, 3).until(EC.presence_of_element_located((By.ID, 'username')))
    username_input.send_keys('abcdef123')

    password_input = browser.find_element(By.ID, 'password')
    password_input.clear()

    current_url = browser.current_url
    login_form = browser.find_element(By.CLASS_NAME, 'login-form-container')

    login_button = browser.find_element(By.ID, 'kc-login')
    login_button.click()

    try:
        WebDriverWait(browser, 2).until(
            lambda driver: driver.current_url != current_url
                           or EC.staleness_of(login_form)(driver)
        )
        raise AssertionError('Кнопка должна быть заблокирована: страница не должна перезагружаться')
    except TimeoutException:
        pass

    try:
        error = WebDriverWait(browser, 3).until(EC.presence_of_element_located((By.ID, 'password-meta')))
        assert 'Введите пароль' in error.text, 'Не было выведено надписи "Введите пароль"'
    except Exception:
        raise AssertionError('Не появилось сообщение "Введите пароль" при пустом поле пароля')


def test_show_hide_password(browser):
    '''TC-003: Проверка кнопки "глаз" для отображения/скрытия пароля'''
    password_input = browser.find_element(By.ID, 'password')
    password_input.send_keys('qwerty123')

    eye_svg = browser.find_element(By.CLASS_NAME, 'rt-input__eye')
    actions = ActionChains(browser)

    actions.move_to_element(eye_svg).click().perform()
    assert password_input.get_attribute('type') == 'text', 'Поле пароля не стало видимым после клика по глазу'

    actions.move_to_element(eye_svg).click().perform()
    assert password_input.get_attribute('type') == 'password', 'Поле пароля не скрывается после второго клика по глазу'


def test_tabs_switch(browser):
    '''TC-004: Проверка кнопок выбора входа (почта, логин и т.д.)'''
    tab_ids = ['t-btn-tab-mail', 't-btn-tab-login', 't-btn-tab-phone', 't-btn-tab-ls']
    for tab_id in tab_ids:
        tab = browser.find_element(By.ID, tab_id)
        tab.click()
        assert 'rt-tab--active' in tab.get_attribute('class'), f'Вкладка {tab_id} не стала активной'


def test_remember_me_checkbox(browser):
    '''TC-005: Проверка чекбокса "Запомнить меня"'''
    checkbox = browser.find_element(By.CLASS_NAME, 'rt-checkbox')
    actions = ActionChains(browser)

    actions.move_to_element(checkbox).click().perform()
    assert 'rt-checkbox--checked' not in checkbox.get_attribute(
        'class'), 'Чекбокс кнопки не перестал быть отмеченным после первого клика'

    actions.move_to_element(checkbox).click().perform()
    assert 'rt-checkbox--checked' in checkbox.get_attribute(
        'class'), 'Чекбокс кнопки не стал отмеченным после второго клика'


def test_login_without_captcha(browser):
    '''TC-006: Вход при вводе всего, кроме капчи'''
    username_input = WebDriverWait(browser, 3).until(EC.presence_of_element_located((By.ID, 'username')))
    username_input.send_keys('abcdef123')

    password_input = browser.find_element(By.ID, 'password')
    password_input.send_keys('TestPassword123')

    current_url = browser.current_url
    login_form = browser.find_element(By.CLASS_NAME, 'login-form-container')

    login_button = browser.find_element(By.ID, 'kc-login')
    login_button.click()

    try:
        WebDriverWait(browser, 2).until(
            lambda d: d.current_url != current_url
                      or EC.staleness_of(login_form)(d)
        )
        raise AssertionError('Кнопка не должна работать без капчи: страница не должна перезагружаться')
    except TimeoutException:
        pass

    try:
        error = WebDriverWait(browser, 3).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'captcha-container'))
        )
        assert 'текст с картинки' in error.text.lower(), 'Не было сообщения о том, что нужно ввести капчу'
    except Exception:
        raise AssertionError('Не появилось сообщение о том, что не пройдена капча')


def test_login_button_blocked_empty_fields(browser):
    '''TC-007: Проверка блокировки кнопки "Войти"'''
    current_url = browser.current_url
    login_button = browser.find_element(By.ID, 'kc-login')
    login_button.click()
    login_form = browser.find_element(By.CLASS_NAME, 'login-form-container')

    try:
        WebDriverWait(browser, 2).until(
            lambda d: d.current_url != current_url
                      or EC.staleness_of(login_form)(d)
        )
        raise AssertionError('Кнопка не должна работать без введеных данных: страница не должна перезагружаться')
    except TimeoutException:
        pass


def test_forgot_password_link(browser):
    '''TC-008: Проверка ссылки "Забыл пароль"'''
    link = browser.find_element(By.LINK_TEXT, 'Забыл пароль')
    link.click()
    assert 'reset' in browser.current_url, 'Кнопка "Забыл пароль" не работает должным образом: не переносит на страницу восстановления'


def test_registration_link(browser):
    '''TC-009: Проверка ссылки "Нет аккаунта? Зарегистрироваться"'''
    link = browser.find_element(By.ID, 'kc-register')
    link.click()
    assert 'registration' in browser.current_url, 'Кнопка "Зарегистрироваться" не работает должным образом: не переносит на страницу восстановления'


def test_phone_field_letters_redirect(browser):
    '''TC-010: Проверка ввода букв в поле авторизации'''
    elements = ['t-btn-tab-phone', 't-btn-tab-mail', 't-btn-tab-ls']

    for el in elements:
        try:
            browser.find_element(By.ID, el).click()
            phone_input = WebDriverWait(browser, 2).until(
                EC.presence_of_element_located((By.ID, 'username'))
            )
            phone_input.clear()
            phone_input.send_keys('abcdef', Keys.ENTER)
            WebDriverWait(browser, 2).until(
                lambda d: d.find_element(By.NAME, 'tab_type').get_attribute('value') == 'LOGIN'
            )
        except Exception:
            raise AssertionError(
                f'Тест не прошел для вкладки {el}: буквы в поле телефона не перенаправили на таб "LOGIN"')


def test_user_agreement_link(browser):
    '''TC-011: Проверка открытия пользовательского соглашения'''
    link = WebDriverWait(browser, 5).until(
        EC.element_to_be_clickable((By.ID, 'rt-auth-agreement-link'))
    )
    link.click()
    WebDriverWait(browser, 5).until(lambda d: len(d.window_handles) > 1)
    browser.switch_to.window(browser.window_handles[-1])
    assert 'agreement' in browser.current_url, 'Ссылка на пользовательское соглашение не открылась'
    browser.switch_to.window(browser.window_handles[0])
