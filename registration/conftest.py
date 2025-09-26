import pytest
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

URL = 'https://b2c.passport.rt.ru/auth/realms/b2c/protocol/openid-connect/auth?client_id=account_b2c&redirect_uri=https://b2c.passport.rt.ru/account_b2c/login&response_type=code&scope=openid&state=faec91f6-8df3-40a1-8916-9e68a4385ba0'


@pytest.fixture(scope='session')
def browser():
    """Открывает браузер один раз на всю сессию тестов и сразу переходит на страницу регистрации"""
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-gpu')
    options.add_argument('--headless')  # можно отключить для визуального режима
    driver = webdriver.Chrome(options=options)
    driver.get(URL)

    # Переход на страницу регистрации
    register_link = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, 'kc-register'))
    )
    register_link.click()
    yield driver
    driver.quit()


@pytest.fixture(autouse=True)
def reset_registration_form(browser):
    """Возвращает форму регистрации в дефолтное состояние"""
    try:
        # Список полей для очистки
        field_ids = ['firstName', 'lastName', 'address', 'password', 'password-confirm']
        for fid in field_ids:
            try:
                field = WebDriverWait(browser, 2).until(
                    EC.visibility_of_element_located((By.ID, fid))
                )
                # Очистка через Ctrl+A + Delete
                field.click()
                ActionChains(browser) \
                    .key_down(Keys.CONTROL).send_keys('a') \
                    .key_up(Keys.CONTROL).send_keys(Keys.DELETE) \
                    .perform()
            except:
                continue  # если поля нет — пропускаем
    except Exception as e:
        pytest.fail(f'Ошибка при сбросе формы регистрации: {e}')
    yield
