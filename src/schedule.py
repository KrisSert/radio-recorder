# This module scrapes the radio schedule from webpage

from params import parameters
import re
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime


class Schedule:
    def __init__(self, schedule_data=None):
        self.schedule_data = schedule_data or []

    @staticmethod
    def get_chrome_options():
        # set Chrome to not open the GUI -- headless
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.binary_location = parameters.chrome_binary_path
        return chrome_options

    @staticmethod
    def create_tuples_of_two(input_list):
        # Using a loop to create tuples of two elements
        return [(input_list[i], input_list[i + 1]) for i in range(0, len(input_list), 2)]

    @property
    def get_schedule(self):
        self.schedule_data = []

        driver = webdriver.Chrome(options=Schedule.get_chrome_options())
        driver.get(parameters.schedule_url)

        try:
            allow_cookies = driver.find_element("xpath", parameters.cookies_button)
            allow_cookies.click()
            schedule_txt = driver.find_element("xpath", parameters.schedule_xpath).text
        except NoSuchElementException as e:
            logging.error(f"Selenium NoSuchElementException: {e}. Recording all shows.")
            return parameters.DEFAULT_SCHEDULE
        finally:
            driver.close()

        # create the schedule_data
        # structure: [show_name, start_time, end_time (datetime.now().strftime("%H:%M:%S.%f"))]
        schedule_tuples = Schedule.create_tuples_of_two(schedule_txt.split("\n"))

        # loop over shows in schedule: create a new schedule w only shows that have a reference in keywords.
        for show_time, show_name in schedule_tuples:
            for key in parameters.show_keywords:
                # ignore shows with '*' (replays)
                if (key in show_name.lower()) and ('*' not in show_name):
                    start_time, end_time = show_time.split('–')
                    self.schedule_data.append([show_name, start_time, end_time])

        return self.schedule_data



#print(Schedule().get_schedule)