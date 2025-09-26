import pytest
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

URL = 'https://b2c.passport.rt.ru/auth/realms/b2c/protocol/openid-connect/auth?client_id=account_b2c&redirect_uri=https://b2c.passport.rt.ru/account_b2c/login&response_type=code&scope=openid&state=faec91f6-8df3-40a1-8916-9e68a4385ba0'


@pytest.fixture(scope="session")
def browser():
    """Открывает браузер один раз на всю сессию тестов"""
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.get(URL)
    yield driver
    driver.quit()


@pytest.fixture(autouse=True)
def reset_state(browser):
    """
    Возвращает форму в дефолтное состояние:
    - вкладка LOGIN
    - очищенные поля
    - снятый чекбокс 'Запомнить меня'
    """
    try:
        if URL != browser.current_url:
            browser.get(URL)
        # Вернуть вкладку LOGIN
        login_tab = WebDriverWait(browser, 5).until(
            EC.element_to_be_clickable((By.ID, "t-btn-tab-login"))
        )
        login_tab.click()

        login_field = WebDriverWait(browser, 5).until(
            EC.visibility_of_element_located((By.ID, "username"))
        )
        login_field.clear()
        # Поле пароля
        password_field = WebDriverWait(browser, 5).until(
            EC.visibility_of_element_located((By.ID, "password"))
        )
        password_field.clear()


        # Снять чекбокс, если отмечен
        try:
            remember_me = browser.find_element(By.NAME, "remember_me")
            if remember_me.is_selected():
                remember_me.click()
        except:
            pass  # вдруг чекбокса нет

    except Exception as e:
        pytest.fail(f"Ошибка при сбросе состояния страницы: {e}")

    yield
    # можно добавить post-cleanup если понадобится
