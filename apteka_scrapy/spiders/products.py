import scrapy
from apteka_scrapy.items import AptekaItem
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re


class ProductsSpider(scrapy.Spider):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.city = "Томск"

    name = "products"
    allowed_domains = ["apteka-ot-sklada.ru"]
    start_urls = [
        "https://apteka-ot-sklada.ru/catalog/medikamenty-i-bady%2Fvitaminy-i-mikroelementy%2Fvitamin-s?start=36",  # Витамин C
        "https://apteka-ot-sklada.ru/catalog/medikamenty-i-bady/vitaminy-i-mikroelementy/vitaminy-dlya-immuniteta",  # Витамины для иммунитета
        "https://apteka-ot-sklada.ru/catalog/medikamenty-i-bady/vitaminy-i-mikroelementy/vitaminy-dlya-glaz"  #  Витамины для глаз
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield SeleniumRequest(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        driver = response.request.meta['driver']
        if response.xpath("//a[contains(@class, 'layout-city__element')]//text()") != self.city:
            # Определяем кнопку смены города
            wait = WebDriverWait(driver, 5)
            element = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//a[contains(@class, 'layout-city__element')]"))
            )
            element.click()
            time.sleep(0.5)  # ожидание подгрузки

            # Определяем поле ввода для города и вводим значение
            city_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@name='city']"))
            )
            city_input.clear()
            city_input.send_keys(self.city)
            time.sleep(0.5)  # ожидание подгрузки
            # Подтверждаем выбор города
            wait = WebDriverWait(driver, 10)
            element = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//ul[@class='layout-city-modal-cities-grid-list']//a"))
            )
            element.click()
            time.sleep(0.5)  # ожидание подгрузки

        # Получаем ссылки на товары
        product_list = response.xpath("//div[contains(@class, 'goods-grid__cell')]")
        for item in product_list:
            href = item.xpath(".//a[@class='goods-card__link']/@href").get()
            tag = str(
                item.xpath(".//span[contains(@class, 'ui-tag')]/text()").get()
            ).strip().replace("\n", "").capitalize()
            product_url = f"https://apteka-ot-sklada.ru{href}"
            yield scrapy.Request(url=product_url, callback=self.parse_product,  meta={'tag': tag})

        # Находим ссылку на другую странциу и переходим по ней
        next_page = response.xpath("//ul[contains(@class, 'pagination')]/li[last()]/a/@href")
        if next_page:
            next_page_url = f"https://apteka-ot-sklada.ru{next_page.get()}"
            yield SeleniumRequest(url=next_page_url, callback=self.parse)

    def parse_product(self, response):
        # Парсим товар
        item = AptekaItem()
        timestamp = time.time()
        url = response.url
        RPC = re.findall(r'\d+', url)[-1]
        title = response.xpath("//h1//text()").get()
        marketing_tags = response.meta.get('tag')
        brand = response.xpath("//span[@itemtype='legalName']/text()").get()
        section_list = response.xpath("//ul[@class='ui-breadcrumbs__list']/li[position() < last()]//text()").getall()
        section = [item for item in section_list if item is not ' ']
        price = str(response.xpath("//div[@class='goods-offer-panel__price']//text()").get()).strip().replace("\n","")
        location = response.xpath("//span[@itemtype='location']/text()").get()
        main_image = response.xpath("//img[contains(@class, 'goods-gallery__picture')]/@src").get()
        text = str(
            "".join(response.xpath("//div[@itemprop='description']/p/text()").getall())
        ).strip()
        description = re.sub(r"[\r\t\n\xa0]", "", text)
        variants = 1
        in_stock = response.xpath("//a[contains(@class, 'ui-link text_weight_bold')]//text()").get()
        if in_stock:
            in_stock = True
        else:
            in_stock = False

        item['timestamp'] = timestamp,
        item['RPC'] = RPC,
        item['url'] = url,
        item['title'] = title,
        item['marketing_tags'] = marketing_tags,
        item['brand'] = brand,
        item['section'] = section,
        item['price'] = price,
        item['in_stock'] = in_stock,
        item['main_image'] = main_image,
        item['description'] = description,
        item['location'] = location,
        item['variants'] = variants
        yield item
