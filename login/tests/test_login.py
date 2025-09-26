import pytest
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains

url = 'https://b2c.passport.rt.ru/auth/realms/b2c/protocol/openid-connect/auth?client_id=account_b2c&redirect_uri=https://b2c.passport.rt.ru/account_b2c/login&response_type=code&scope=openid&state=faec91f6-8df3-40a1-8916-9e68a4385ba0'


def test_login_empty_username(browser):
    browser.get(url)
    # Поле пароля
    password_input = WebDriverWait(browser, 3).until(EC.presence_of_element_located((By.ID, "password")))
    password_input.send_keys("TestPassword123")

    # Кнопка Войти
    login_button = browser.find_element(By.ID, "kc-login")
    login_button.click()

    # Сохраняем текущий URL
    current_url = browser.current_url

    # --- добавлено: сохраняем ссылку на форму, чтобы отследить её "протухание" ---
    login_form = browser.find_element(By.CLASS_NAME, "login-form-container")

    # Кнопка Войти
    login_button = browser.find_element(By.ID, "kc-login")
    login_button.click()
    try:
        error = WebDriverWait(browser, 3).until(EC.presence_of_element_located((By.ID, "username-meta")))
        assert "Введите логин" in error.text, 'Не было выведено надписи "Введите логин"'
    except Exception:
        raise AssertionError('Не появилось сообщение "Введите логин" при пустом поле логина')

    try:
        WebDriverWait(browser, 2).until(
            lambda driver: driver.current_url != current_url
                           or EC.staleness_of(login_form)(driver)
        )
        # Если этот wait сработал, значит кнопка пыталась что-то сделать — FAIL
        raise AssertionError("Кнопка должна быть заблокирована: страница не должна перезагружаться")
    except TimeoutException:
        # Всё ок — страница не изменилась, элемент остался
        pass


def test_login_empty_password(browser):
    # Логин
    username_input = WebDriverWait(browser, 3).until(EC.presence_of_element_located((By.ID, "username")))
    username_input.send_keys("abcdef123")

    # Поле пароля пустое
    password_input = browser.find_element(By.ID, "password")
    password_input.clear()

    # Сохраняем текущий URL
    current_url = browser.current_url

    # --- добавлено: сохраняем ссылку на форму, чтобы отследить её "протухание" ---
    login_form = browser.find_element(By.CLASS_NAME, "login-form-container")

    login_button = browser.find_element(By.ID, "kc-login")
    login_button.click()

    try:
        WebDriverWait(browser, 2).until(
            lambda driver: driver.current_url != current_url
                           or EC.staleness_of(login_form)(driver)
        )
        # Если этот wait сработал, значит кнопка пыталась что-то сделать — FAIL
        raise AssertionError("Кнопка должна быть заблокирована: страница не должна перезагружаться")
    except TimeoutException:
        # Всё ок — страница не изменилась, элемент остался
        pass

    try:
        error = WebDriverWait(browser, 3).until(EC.presence_of_element_located((By.ID, "password-meta")))
        assert "Введите пароль" in error.text, 'Не было выведено надписи "Введите пароль"'
    except Exception:
        raise AssertionError('Не появилось сообщение "Введите пароль" при пустом поле пароля')


def test_show_hide_password(browser):
    password_input = browser.find_element(By.ID, "password")
    password_input.send_keys("qwerty123")

    # Находим SVG глаза
    eye_svg = browser.find_element(By.CLASS_NAME, "rt-input__eye")

    actions = ActionChains(browser)

    # Первый клик — показываем пароль
    actions.move_to_element(eye_svg).click().perform()
    assert password_input.get_attribute("type") == "text", "Поле пароля не стало видимым после клика по глазу"

    # Второй клик — скрываем пароль
    actions.move_to_element(eye_svg).click().perform()
    assert password_input.get_attribute("type") == "password", "Поле пароля не скрывается после второго клика по глазу"


def test_tabs_switch(browser):
    tab_ids = ["t-btn-tab-mail", "t-btn-tab-login", "t-btn-tab-phone", "t-btn-tab-ls"]

    for tab_id in tab_ids:
        tab = browser.find_element(By.ID, tab_id)
        tab.click()
        # Проверяем, что вкладка активная
        assert "rt-tab--active" in tab.get_attribute("class"), f"Вкладка {tab_id} не стала активной"


def test_remember_me_checkbox(browser):
    checkbox = browser.find_element(By.CLASS_NAME, "rt-checkbox")

    actions = ActionChains(browser)

    # Первый клик — отмечаем
    actions.move_to_element(checkbox).click().perform()
    assert "rt-checkbox--checked" not in checkbox.get_attribute(
        "class"), "Чекбокс кнопки не перестал быть отмеченным после первого клика"

    # Второй клик — снимаем отметку
    actions.move_to_element(checkbox).click().perform()
    assert "rt-checkbox--checked" in checkbox.get_attribute(
        "class"), "Чекбокс кнопки не стал отмеченным после второго клика"


def test_login_without_captcha(browser):
    username_input = WebDriverWait(browser, 3).until(EC.presence_of_element_located((By.ID, "username")))
    username_input.send_keys("abcdef123")

    # Ввод пароля
    password_input = browser.find_element(By.ID, "password")
    password_input.send_keys("TestPassword123")

    # Сохраняем текущий URL
    current_url = browser.current_url

    # Сохраняем ссылку на форму (нам нужно отследить её "протухание")
    login_form = browser.find_element(By.CLASS_NAME, "login-form-container")

    # Кнопка "Войти"
    login_button = browser.find_element(By.ID, "kc-login")
    login_button.click()

    try:
        # Подождём либо навигацию по URL, либо когда старый login_form станет "stale" (пересоздан/удалён)
        WebDriverWait(browser, 2).until(
            lambda d: d.current_url != current_url
                      or EC.staleness_of(login_form)(d)
        )
        # Если until вернул True — значит была навигация или форма пересоздалась -> FAIL
        raise AssertionError("Кнопка не должна работать без капчи: страница не должна перезагружаться")
    except TimeoutException:
        # Всё ок — страница осталась той же (ни навигации, ни протухания формы)
        pass

    # Проверяем наличие ошибки про капчу
    try:
        error = WebDriverWait(browser, 3).until(
            EC.presence_of_element_located((By.CLASS_NAME, "captcha-container"))
        )
        assert "текст с картинки" in error.text.lower(), 'Не было сообщения о том, что нужно ввести капчу'
    except Exception:
        raise AssertionError("Не появилось сообщение о том, что не пройдена капча")

def test_login_button_blocked_empty_fields(browser):
    # Сохраняем текущий URL
    current_url = browser.current_url

    # Кнопка "Войти"
    login_button = browser.find_element(By.ID, "kc-login")
    login_button.click()

    # Сохраняем ссылку на форму (нам нужно отследить её "протухание")
    login_form = browser.find_element(By.CLASS_NAME, "login-form-container")

    try:
        # Подождём либо навигацию по URL, либо когда старый login_form станет "stale" (пересоздан/удалён)
        WebDriverWait(browser, 2).until(
            lambda d: d.current_url != current_url
                      or EC.staleness_of(login_form)(d)
        )
        # Если until вернул True — значит была навигация или форма пересоздалась -> FAIL
        raise AssertionError("Кнопка не должна работать без введеных данных: страница не должна перезагружаться")
    except TimeoutException:
        # Всё ок — страница осталась той же (ни навигации, ни протухания формы)
        pass

def test_forgot_password_link(browser):
    link = browser.find_element(By.LINK_TEXT, "Забыл пароль")
    link.click()
    assert "reset" in browser.current_url, 'Кнопка "Забыл пароль" не работает должным образом: не переносит на страницу восстановления'


def test_registration_link(browser):
    link = browser.find_element(By.ID, "kc-register")
    link.click()
    assert "registration" in browser.current_url, 'Кнопка "Зарегистрироваться" не работает должным образом: не переносит на страницу восстановления'


def test_phone_field_letters_redirect(browser):
    browser.get(url)

    elements = ['t-btn-tab-phone', 't-btn-tab-mail', 't-btn-tab-ls']

    for el in elements:
        try:
            # Переключаемся на вкладку
            browser.find_element(By.ID, el).click()

            # Вводим буквы в поле телефона на форме логина
            phone_input = WebDriverWait(browser, 2).until(
                EC.presence_of_element_located((By.ID, 'username'))
            )
            phone_input.clear()
            phone_input.send_keys('abcdef', Keys.ENTER)


            WebDriverWait(browser, 2).until(
                lambda d: d.find_element(By.NAME, "tab_type").get_attribute("value") == "LOGIN"
            )


        except Exception:
            raise AssertionError(f'Тест не прошел для вкладки {el}: буквы в поле телефона не перенаправили на таб "LOGIN"')


def test_user_agreement_link(browser):
    """TC-011 Проверка открытия пользовательского соглашения"""
    link = WebDriverWait(browser, 5).until(
        EC.element_to_be_clickable((By.ID, "rt-auth-agreement-link"))
    )
    link.click()

    # ждём новую вкладку
    # не как в 9 тесте, т.к target="_blank"
    WebDriverWait(browser, 5).until(lambda d: len(d.window_handles) > 1)

    # переключаемся на последнюю
    browser.switch_to.window(browser.window_handles[-1])
    assert "agreement" in browser.current_url, "Ссылка на пользовательское соглашение не открылась"

    # возвращаемся в первую вкладку
    browser.switch_to.window(browser.window_handles[0])


