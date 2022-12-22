import re

from scrapy.spiders import SitemapSpider
import json
from datetime import datetime


class AdidasSpider(SitemapSpider):
    url = "https://www.adidas.mx/on/demandware.static/-/Sites-CustomerFileStore/default/adidas-MX/es_MX/sitemaps/product/adidas-MX-es-mx-product.xml"
    name = "adidas"
    sitemap_urls = [url]
    sitemap_rules = [('.html', 'parse_product')]


    def parse_product(self, response):
        details_json = response.xpath("//script[contains(@type,'json')]/text()").extract_first()
        details_dict = json.loads(details_json)

        json_file = re.findall(r'JSON.parse\((.*)\)', response.text)[0]
        
        # remove trailing semicolon
        # load the json file as a dictionary
        json_data = json.loads(json_file)
        result_dict = json.loads(json_data)

        product_list = result_dict['productStore']['products']
        for product,value in product_list.items():
            data = value.get('data')
            product_name = data.get('name')
            product_description = data.get('product_description',{})
            description_text = product_description.get('text')
            subtitle = product_description.get('subtitle')
            detalles = product_description.get('usps')
            color = data.get('attribute_list',{}).get('color',{})
            sku = data.get('id')
            brand_name = details_dict.get('brand',{}).get('name')
            price = details_dict.get('offers',{}).get('price')
            availability = details_dict.get('offers',{}).get('availability')
            breadcrumb_list =[ x.get('text') for x in data.get('breadcrumb_list',[])]
            images = details_dict.get('image',[])
            price_dict = data.get('pricing_information',{})
            sale_price = price_dict.get('currentPrice')
            price = price_dict.get('standard_price')
            item = {}
            item['Date'] = datetime.now().strftime('%d/%m/%Y')
            item['Canal'] = 'Adidas'
            categories_dict = {x:y for x,y in enumerate(breadcrumb_list)}
            item['Category'] = categories_dict.get(0)
            item['Subcategory'] = categories_dict.get(1)
            item['Subcategory2'] = categories_dict.get(2)
            item['Subcategory3'] = ''
            item['Marca'] = brand_name
            item['Modelo'] = data.get('model_number')
            item['SKU'] = sku
            item['UPC'] = sku
            item['Item'] = product_name
            item['Item Characteristics'] = {subtitle: description_text, 'Detalles': detalles, 'Color del artículo': color, 'SKU': sku}
            item['URL SKU'] = response.url
            item['Image'] =  images[0]
            item['Price'] = price
            item['Sale Price'] = sale_price
            item['Shipment Cost'] = ''
            item['Sales Flag'] = ''
            item['Store ID'] = ''
            item['Store Name'] = ''
            item['Store Address'] = ''
            item['Stock'] = availability
            item['UPC WM'] = sku[0:-1].zfill(16)
            item['Final Price'] = min(price, sale_price) if sale_price else price
            yield item

