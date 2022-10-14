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

from telegrambot import send_message


def driver():
    options = Options()
    options.add_argument("start-maximized")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--headless")
    options.add_argument("--use-fake-ui-for-media-stream")
    options.add_argument("--use-fake-device-for-media-stream")
    return webdriver.Chrome(executable_path="./chromedriver", options=options)


def login_app(
    chat_id=None,
    action=None,
    userid="991483728",
    password=os.environ.get("POSHADIR_PASSWORD"),
):
    try:
        driver.get("https://hadir.posindonesia.co.id/pos_hadir/01/index.php")
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
        title = alert_container.find_element(By.TAG_NAME, "h2").text
        subtitle = alert_container.find_element(By.TAG_NAME, "p").text
        alert_message = {"title": title, "subtitle": subtitle}
        logger.debug(alert_message)

        if title == "[ Konfirmasi ]":
            logger.debug("%s not logged in", userid)
            wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[@class='cancel'][normalize-space()='Tidak']")
                ),
                "alert_button",
            ).click()

            message = "Anda tidak bisa melakukan absensi dikarenakan sedang cuti"
            send_message(chat_id, message)
            driver.quit()
        else:
            wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[@class='confirm'][normalize-space()='OK']")
                ),
                "alert_button",
            ).click()

            if subtitle == "Login Berhasil":
                logger.debug("%s is logged in", userid)
                if action == "check_in":
                    action_app(chat_id, "bmasuk")
                elif action == "check_out":
                    action_app(chat_id, "bpulang")
                else:
                    logger.debug("no action selected")
                    driver.quit()
            elif subtitle.startswith("Login Gagal"):
                logger.debug("userid or password is not valid")
                message = "User ID atau Password salah"
                send_message(chat_id, message)
                driver.quit()
            else:
                logger.debug(f"unexpected alert is occurs at {login_app.__name__}")
                driver.quit()
    except Exception as e:
        message = f"unexpected error is occurs at {login_app.__name__}"
        logger.debug(message)
        logger.exception(e)
        driver.quit()
        send_message(chat_id, message.capitalize())


def logout_app(chat_id=None, message=None):
    try:
        driver.find_element(
            By.XPATH, "//a[@class='nav-link active'][normalize-space()='Logout']"
        ).click()
        time.sleep(2)
        driver.find_element(
            By.XPATH, "//button[@class='confirm'][normalize-space()='Ya']"
        ).click()
        logger.debug("logged out")
    except Exception as e:
        logger.debug("unexpected error is occurs at %s", logout_app.__name__)
        logger.exception(e)
    finally:
        driver.quit()
        send_message(chat_id, message.capitalize())


def action_app(chat_id, button_id):
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
            # message = "already check in before"
            message = "anda sudah melakukan absensi masuk"
            logger.debug(message)
        else:
            # message = "could not access webcam"
            message = "perangkat webcam tidak ditemukan"
            logger.debug(message)

        logout_app(chat_id, message)
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

            action = "absensi datang" if button_id == "bmasuk" else "absensi pulang"
            s = subtitle.split(" : ")
            message = f"{action} berhasil pada pukul {s[1]}"
            logger.debug("%s is succeed", action)

            logout_app(chat_id, message)
        elif e.msg == "button":
            logger.debug("timeout exception from message 'button'")
            action_app(chat_id, button_id)
        else:
            message = f"timeout exception at {action_app.__name__}"
            logger.debug(message)

            logout_app(chat_id, message)
    except Exception as e:
        message = f"unexpected error is occurs at {action_app.__name__}"
        logger.debug(message)
        logger.exception(e)
        driver.quit()
        send_message(chat_id, message.capitalize())


if __name__ != "__main__":
    logger = logging.getLogger(__name__)
    driver = driver()
    wait = WebDriverWait(driver, 5)
