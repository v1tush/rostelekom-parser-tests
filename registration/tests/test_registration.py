import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

URL = 'https://b2c.passport.rt.ru/auth/realms/b2c/protocol/openid-connect/auth?client_id=account_b2c&redirect_uri=https://b2c.passport.rt.ru/account_b2c/login&response_type=code&scope=openid&state=faec91f6-8df3-40a1-8916-9e68a4385ba0'


# ------------------ FIXTURES ------------------

@pytest.fixture(scope="session")
def browser():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.get(URL)

    # Переходим сразу на страницу регистрации
    register_link = WebDriverWait(driver, 3).until(
        EC.element_to_be_clickable((By.ID, "kc-register"))
    )
    register_link.click()
    yield driver
    driver.quit()


# ------------------ TESTS ------------------

# Находим кнопку "Зарегистрироваться" и кликаем
@pytest.mark.parametrize("text, expected_error", [
    ("user@com", "@email.ru"),
    ('+99999999999', '+7')])
def test_empty_fields_registration(browser, text, expected_error):
    """ TC-012 + TC-013 """
    el = WebDriverWait(browser, 2).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "email-phone"))
    )

    email_input = el.find_element(By.ID, "address")
    email_input.clear()
    email_input.send_keys(text)
    email_input.send_keys(Keys.ENTER)

    # Ищем ошибку внутри того же контейнера
    error_element = WebDriverWait(el, 2).until(
        EC.visibility_of_element_located(
            (By.CLASS_NAME, "rt-input-container__meta--error")
        )
    )

    assert expected_error in error_element.text.lower().strip(), \
        f"Отсутствует фильтрация формата введенных данных(номер или почта), получили '{error_element.text}'"


@pytest.mark.parametrize("password, expected_error", [
    ("qwerty123!", "заглавную"),  # TC-014
    ("QWERTY123!", "строчную"),  # TC-015
    ("Qwerty!@#", "цифру"),  # TC-016
    ("Qwerty123", "спецсимвол"),  # TC-017
    ("Qwe12!", "не менее 8 символов"),  # TC-018
    ("Q" * 200, "не более 20 символов"),  # TC-019
])
def test_registration_password_validation(browser, password, expected_error):
    # Находим контейнер нового пароля
    el = WebDriverWait(browser, 2).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "new-password-container"))
    )

    # Ищем input пароля внутри контейнера
    password_input = el.find_element(By.ID, "password")
    password_input.clear()
    password_input.send_keys(password)
    password_input.send_keys(Keys.ENTER)

    # Ищем ошибку внутри того же контейнера
    error_element = WebDriverWait(el, 2).until(
        EC.visibility_of_element_located(
            (By.CLASS_NAME, "rt-input-container__meta--error")
        )
    )

    assert expected_error in error_element.text.lower().strip(), \
        f"Ожидалось '{expected_error}', но получили '{error_element.text}'"

def test_back_to_login_link(browser):
    """TC-20 Проверка ссылки 'Вернуться к авторизации'"""
    # Находим и кликаем "Вернуться к авторизации"
    back_link = WebDriverWait(browser, 3).until(
        EC.element_to_be_clickable((By.ID, "reset-back"))
    )
    back_link.click()

    # Проверяем, что оказались на странице авторизации
    assert "auth" in browser.current_url, (
        "Ссылка 'Вернуться к авторизации' не работает: не переносит на страницу логина"
    )