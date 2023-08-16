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
