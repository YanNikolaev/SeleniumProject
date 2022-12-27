import pytest
import hashlib
from selenium import webdriver
from selenium.common import ElementNotInteractableException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from settings import valid_email, valid_password



def wait(driver, sec):
    return WebDriverWait(driver, sec)

@pytest.fixture(scope="session")
def get_data():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--window-size=1400,1000')
    driver = webdriver.Chrome('/Users/yan/Desktop/test/chromedriver')
    driver.get("https://petfriends.skillfactory.ru/")
    driver.implicitly_wait(2)
    wait(driver, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[class$='btn-success']"))).click()
    wait(driver, 2).until(EC.presence_of_element_located((By.XPATH, "//a[@href='/login']"))).click()
    wait(driver, 2).until(EC.presence_of_element_located((By.ID, 'email'))).send_keys(valid_email)
    driver.find_element(By.ID, "pass").send_keys(valid_password)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    wait(driver, 2).until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/my_pets')]"))).click()
    user_info = driver.find_elements(By.XPATH, "//div[contains(@class, 'left')]")
    my_pets = driver.find_elements(By.XPATH, "//tbody//tr")
    yield user_info, my_pets
    driver.quit()

class TestPetfriends():

    def test_count_pets(self, get_data):
        """Поверка соответствия количества питомцев указанных в информации пользователя с их реальным количеством"""
        user_info, my_pets = get_data
        list_user_info = user_info[0].text.split("\n")
        count_pets_in_user_info = list_user_info[1]
        count_pets_in_user_info = int(count_pets_in_user_info[count_pets_in_user_info.find(":") + 1:].replace(" ", ""))
        assert count_pets_in_user_info == len(my_pets)


    def test_half_of_pets_without_photos(self, get_data):
        """Проверка на то, что хотя бы половина питомцев имеет фото"""
        _, my_pets = get_data
        count_with_photo = 0
        count_without_photo = 0
        for item in my_pets:
            if item.find_element(By.XPATH, "th//img").get_attribute('src') == " ":
                count_without_photo += 1
            else:
                count_with_photo += 1
        assert count_with_photo > count_without_photo

    def test_pet_info(self, get_data):
        """Проверка на то, что у всех питомцев есть имя, возраст и порода"""
        _, my_pets = get_data
        there_is_a_name_breed_age = True
        for i in range(len(my_pets)):
            if not there_is_a_name_breed_age:
                break
            for j in range(1, 4):
                if my_pets[i].find_element(By.XPATH, "td[{}]".format(j)).text == "":
                    there_is_a_name_breed_age = False
                    break
        assert there_is_a_name_breed_age

    def test_pets_names_are_different(self, get_data):
        """Проверка на то, что у всех питомцев разные имена"""
        _, my_pets = get_data
        names_different = True
        list_of_names = []
        for i in range(len(my_pets)):
            name = my_pets[i].find_element(By.XPATH, "td[1]").text
            if name in list_of_names:
                names_different = False
                break
            list_of_names.append(name)
        assert names_different

    def test_there_are_not_repeating_pets_in_the_list(self, get_data):
        """Проверка на то, что все питомцы уникальны"""
        _, my_pets = get_data
        there_are_not_repeating_pets_in_the_list = True
        list_data = []
        for i in range(len(my_pets)):
            if not there_are_not_repeating_pets_in_the_list:
                break
            string = my_pets[i].find_element(By.XPATH, "th//img").get_attribute('src')
            for j in range(1, 4):
                string += my_pets[i].find_element(By.XPATH, "td[{}]".format(j)).text
            hash_string = hashlib.md5(string.encode())
            hash_dig = hash_string.hexdigest()
            if hash_dig in list_data:
                there_are_not_repeating_pets_in_the_list = False
                list_data.append(hash_dig)
                break
            list_data.append(hash_dig)
        assert there_are_not_repeating_pets_in_the_list