#!/usr/bin/env pipenv-shebang
import datetime
import logging
import os
import time

import pretty_errors
import yaml
from selenium import webdriver
from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from telegrambot import PASSWORD, URL, USERID, send_message


def driver():
    path = os.path.join(os.path.dirname(__file__), "chromedriver")
    options = Options()
    options.add_argument("start-maximized")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--headless")
    options.add_argument("--use-fake-ui-for-media-stream")
    options.add_argument("--use-fake-device-for-media-stream")
    return webdriver.Chrome(executable_path=path, options=options)


def login_app(userid=USERID, password=PASSWORD, action=None):
    try:
        driver.get(URL)
        time.sleep(5)
        driver.find_element(By.ID, "userid").send_keys(userid)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "blogin").click()
        login_data = {"userid": userid, "password": password}
        logger.debug(login_data)

        alert_container = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//div[@class='sweet-alert showSweetAlert visible']")
            ),
            "alert_container",
        )
        # alert_container = driver.find_element(
        #     By.XPATH, "//div[@class='sweet-alert showSweetAlert visible']"
        # )
        title = alert_container.find_element(By.TAG_NAME, "h2").text
        subtitle = alert_container.find_element(By.TAG_NAME, "p").text
        alert_message = {"title": title, "subtitle": subtitle}
        logger.debug(alert_message)

        if title == "[ Konfirmasi ]":
            logger.info("%s not logged in", userid)
            # alert_container.find_element(
            #     By.XPATH, "//button[@class='cancel'][normalize-space()='Tidak']"
            # ).click()
            wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[@class='cancel'][normalize-space()='Tidak']")
                ),
                "alert_button",
            ).click()
            driver.quit()
        else:
            # alert_container.find_element(
            #     By.XPATH, "//button[@class='confirm'][normalize-space()='OK']"
            # ).click()
            wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[@class='confirm'][normalize-space()='OK']")
                ),
                "alert_button",
            ).click()

            if subtitle == "Login Berhasil":
                logger.info("%s is logged in", userid)
                if action == "checkin":
                    action_app("bmasuk")
                elif action == "checkout":
                    action_app("bpulang")
                else:
                    logger.info("no action selected")
                    driver.quit()
            else:
                driver.quit()
    except Exception as e:
        message = f"unexpected error is occurs at {login_app.__name__}"
        logger.info(message)
        logger.exception(e)
        driver.quit()
        send_message(text=message.capitalize())


def logout_app(message=None):
    try:
        driver.find_element(
            By.XPATH, "//a[@class='nav-link active'][normalize-space()='Logout']"
        ).click()
        time.sleep(2)
        driver.find_element(
            By.XPATH, "//button[@class='confirm'][normalize-space()='Ya']"
        ).click()
        logger.info("logged out")
    except Exception as e:
        logger.info("unexpected error is occurs at %s", logout_app.__name__)
        logger.exception(e)
    finally:
        driver.quit()
        send_message(text=message.capitalize())


def action_app(button_id):
    try:
        button = wait.until(EC.element_to_be_clickable((By.ID, button_id)), "button")
        text = button.text
        text = text.strip()
        button.click()
        logger.debug("button '%s' is clicked", text)

        alert_container = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//div[@class='sweet-alert showSweetAlert visible']")
            ),
            "alert_container",
        )
        title = alert_container.find_element(By.TAG_NAME, "h2").text
        subtitle = alert_container.find_element(By.TAG_NAME, "p").text
        alert_message = {"title": title, "subtitle": subtitle}
        alert_container.find_element(
            By.XPATH, "//button[@class='confirm'][normalize-space()='OK']"
        ).click()
        logger.debug(alert_message)

        if title == "":
            message = "already check in before"
            logger.info(message)
        else:
            message = "could not access webcam"
            logger.info(message)

        logout_app(message)
    except (TimeoutException) as e:
        if e.msg == "alert_container":
            logger.debug("timeout exception from message 'alert_container'")
            button = driver.find_element(
                By.XPATH,
                "//button[@class='btn btn-secondary'][@id='ambilgambar']",
            )
            text = button.text
            text = text.strip()
            button.click()
            logger.debug("button '%s' is clicked", text)
            time.sleep(2)

            button = driver.find_element(
                By.XPATH, "//button[@class='btn btn-primary'][@id='ambilgambar']"
            )
            text = button.text
            text = text.strip()
            button.click()
            logger.debug("button '%s' is clicked", text)
            time.sleep(2)

            alert_container = driver.find_element(
                By.XPATH, "//div[@class='sweet-alert showSweetAlert visible']"
            )
            title = alert_container.find_element(By.TAG_NAME, "h2").text
            subtitle = alert_container.find_element(By.TAG_NAME, "p").text
            alert_message = {"title": title, "subtitle": subtitle}
            alert_container.find_element(
                By.XPATH, "//button[@class='confirm'][normalize-space()='OK']"
            ).click()
            logger.debug(alert_message)

            action = "check in" if button_id == "bmasuk" else "check out"
            s = subtitle.split(" : ")
            message = f"{action} is success at {s[1]}"
            logger.info("%s is succeed", action)

            logout_app(message)
        elif e.msg == "button":
            logger.debug("timeout exception from message 'button'")
            action_app(button_id)
        else:
            message = f"timeout exception at {action_app.__name__}"
            logger.info(message)

            logout_app(message)
    except Exception as e:
        message = f"unexpected error is occurs at {action_app.__name__}"
        logger.info(message)
        logger.exception(e)
        driver.quit()
        send_message(text=message.capitalize())


if __name__ != "__main__":
    logger = logging.getLogger(__name__)
    driver = driver()
    wait = WebDriverWait(driver, 5)
