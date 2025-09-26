import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


@pytest.mark.parametrize('text, expected_error', [
    ('user@com', '@email.ru'),  # TC-012
    ('+99999999999', '+7')  # TC-013
])
def test_empty_fields_registration(browser, text, expected_error):
    """TC-012 + TC-013: Проверка ввода некорректного email/телефона"""
    container = WebDriverWait(browser, 2).until(
        EC.visibility_of_element_located((By.CLASS_NAME, 'email-phone'))
    )

    email_input = container.find_element(By.ID, 'address')
    email_input.clear()
    email_input.send_keys(text)
    email_input.send_keys(Keys.ENTER)

    error_element = WebDriverWait(container, 2).until(
        EC.visibility_of_element_located((By.CLASS_NAME, 'rt-input-container__meta--error'))
    )

    assert expected_error in error_element.text.lower().strip(), \
        f"Отсутствует фильтрация формата введенных данных, получили '{error_element.text}'"


@pytest.mark.parametrize('password, expected_error', [
    ('qwerty123!', 'заглавную'),  # TC-014
    ('QWERTY123!', 'строчную'),  # TC-015
    ('Qwerty!@#', 'цифру'),  # TC-016
    ('Qwerty123', 'спецсимвол'),  # TC-017
    ('Qwe12!', 'не менее 8 символов'),  # TC-018
    ('Q' * 200, 'не более 20 символов')  # TC-019
])
def test_registration_password_validation(browser, password, expected_error):
    """TC-014..TC-019: Проверка валидации пароля при регистрации"""
    container = WebDriverWait(browser, 2).until(
        EC.visibility_of_element_located((By.CLASS_NAME, 'new-password-container'))
    )

    password_input = container.find_element(By.ID, 'password')
    password_input.clear()
    password_input.send_keys(password)
    password_input.send_keys(Keys.ENTER)

    error_element = WebDriverWait(container, 2).until(
        EC.visibility_of_element_located((By.CLASS_NAME, 'rt-input-container__meta--error'))
    )

    assert expected_error in error_element.text.lower().strip(), \
        f"Ожидалось '{expected_error}', но получили '{error_element.text}'"


def test_back_to_login_link(browser):
    """TC-020: Проверка ссылки 'Вернуться к авторизации'"""
    back_link = WebDriverWait(browser, 3).until(
        EC.element_to_be_clickable((By.ID, 'reset-back'))
    )
    back_link.click()

    assert 'auth' in browser.current_url, \
        "Ссылка 'Вернуться к авторизации' не работает: не переносит на страницу логина"
