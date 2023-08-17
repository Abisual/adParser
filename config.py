# config.py

# Запрос для поиска
query = "/toyota/supra/"

# XPath для контейнера объявлений
container_xpath = "(//div[@class='css-1nvf6xk eojktn00'])[1]"

# XPath для заголовков объявлений
title_xpath = "//span[@data-ftid='bull_title']"

# XPath для цен объявлений
price_xpath = "//span[@data-ftid='bull_price']"

# XPath для ссылок объявлений
link_xpath = "//span[@data-ftid='bull_title']/ancestor::a"

# XPath для описаний объявлений (контейнер)
description_xpath = ".//div[@data-ftid='component_inline-bull-description']"

# XPath для описаний объявлений
description_parts_xpath = ".//span[@data-ftid='bull_description-item']//text()"

# Список User-Agent
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.3"
]

