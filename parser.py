import csv
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class CianSeleniumParser:
    def __init__(self, headless=True):
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )

        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def parse_flats(self, url, max_pages=5):
        """Парсит объявления с пагинацией"""
        all_flats = []

        for page in range(1, max_pages + 1):
            page_url = f"{url}&p={page}"
            self.driver.get(page_url)
            time.sleep(3)

            cards = self.wait.until(
                EC.presence_of_all_elements_located(
                    (
                        By.CLASS_NAME,
                        "x31de4314--f31226--cont",
                    )
                )
            )

            for card in cards:
                print(f"Page {page}, card {cards.index(card) + 1}")
                try:
                    flat = {}

                    price = card.find_element(
                        By.CSS_SELECTOR,
                        ".x31de4314--_7735e--color_text-primary-default.x31de4314--_2697e--lineHeight_7u.x31de4314--_2697e--fontWeight_bold.x31de4314--_2697e--fontSize_22px.x31de4314--_17731--display_block.x31de4314--dc75cc--text",
                    )
                    flat["price"] = price.text

                    address = card.find_element(
                        By.CLASS_NAME, "x31de4314--_42135--labels"
                    )
                    address_arr = address.text.split(", ")
                    flat["city"] = address_arr[0]
                    flat["region"] = address_arr[1]
                    flat["district"] = address_arr[2]
                    flat["metro"] = address_arr[3] if len(address_arr) > 3 else None
                    flat["address"] = ", ".join(address_arr[4:]) if len(address_arr) > 4 else None

                    title_arr = card.find_elements(
                        By.CSS_SELECTOR,
                        ".x31de4314--_7735e--color_text-main-default.x31de4314--_2697e--lineHeight_28px.x31de4314--_2697e--fontWeight_bold.x31de4314--_2697e--fontSize_22px.x31de4314--_17731--display_block.x31de4314--dc75cc--text",
                    )
                    title = title_arr[0].text if title_arr else card.find_element(
                        By.CSS_SELECTOR,
                        ".x31de4314--_7735e--color_text-primary-default.x31de4314--_2697e--lineHeight_28px.x31de4314--_2697e--fontWeight_bold.x31de4314--_2697e--fontSize_22px.x31de4314--_17731--display_block.x31de4314--dc75cc--text.x31de4314--dc75cc--text_letterSpacing__normal",
                    ).text
                    sub_arr = card.find_elements(
                        By.CSS_SELECTOR,
                        ".x31de4314--_7735e--color_text-primary-default.x31de4314--_2697e--lineHeight_22px.x31de4314--_2697e--fontWeight_bold.x31de4314--_2697e--fontSize_16px.x31de4314--_17731--display_block.x31de4314--dc75cc--text",
                    )
                    sub = sub_arr[0].text if sub_arr else ""
                    flat["area"] = title.split(", ")[1].split(" ")[0] if "м²," in title else sub.split(", ")[1].split(" ")[0]
                    flat["floor"] = title.split(", ")[2].split("/")[0] if "м²," in title else sub.split(", ")[2].split("/")[0]
                    flat["max_floor"] = title.split(", ")[2].split("/")[1].split(" ")[0] if "м²," in title else sub.split(", ")[2].split("/")[1].split(" ")[0]
                    rooms = title.split(", ")[0].split("-")[0] if "м²," in title else sub.split(", ")[0].split("-")[0]
                    if not any(char.isdigit() for char in rooms):
                        flat["rooms"] = "Студия"
                    else:
                        flat["rooms"] = rooms

                    link = card.find_element(By.CLASS_NAME, "x31de4314--_2c422--link")
                    flat["url"] = link.get_attribute("href")

                    all_flats.append(flat)

                except Exception as e:
                    print(f"Ошибка при парсинге карточки: {e}")
                    continue

            print(f"Страница {page}: найдено {len(cards)} объявлений")

        return all_flats

    def close(self):
        self.driver.quit()


parser = CianSeleniumParser(headless=False)
flats = parser.parse_flats(
    "https://www.cian.ru/cat.php?deal_type=sale&offer_type=flat&region=2", max_pages=40
)
fieldnames = ["price", "city", "region", "district", "metro", "address", "area", "floor", "max_floor", "rooms", "url"]
with open("flats.csv", mode="w", newline="", encoding="utf-8-sig") as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=";")
    writer.writeheader()
    writer.writerows(flats)
parser.close()
