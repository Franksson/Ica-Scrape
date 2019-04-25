import requests
import json
import re
import csv

class product_item():
    def __init__(self, name, origin, nutrition, price, price_code):
        self.name = name
        self.origin = origin
        self.nutrition = nutrition
        self.price = price
        self.price_code = price_code

    def __repr__(self):
        string = self.name + self.origin + self.nutrition.__repr__() + self.price.__str__() + self.price_code
        return string

def parse_nutrition(string):
    kcal = 0
    fat = 0
    carbs = 0
    protein = 0

    cats = string.split(", ")
    for cat in cats:
        val = cat.split()
        if (val[0] == 'Fett'):
            fat = float(re.findall(r'\d+', val[1])[0])
        elif (val[0] == 'Protein'):
            protein = float(re.findall(r'\d+', val[1])[0])
        elif (val[0] == 'Kolhydrater'):
            carbs = float(re.findall(r'\d+', val[1])[0])
        elif (val[1] == '(kcal)'):
            kcal = float(re.findall(r'\d+', val[2])[0])
    return (kcal, fat, carbs, protein)



def write_csv(title, products):
    with open(title, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(['Namn', 'Land', 'Kcal', 'Fett', 'Kolhydrater', 'Protein', 'Pris/KG', 'Jämnförelse'])
        for prod in products:
            writer.writerow([
                    prod.name,
                    prod.origin,
                    prod.nutrition[0],
                    prod.nutrition[1],
                    prod.nutrition[2],
                    prod.nutrition[3],
                    prod.price,
                    prod.price_code
                ])

def get_all():
    cat_ids = ['kott--fagel---fisk-id_1', 'vegetariskt-id_2233', 'fryst-id_628', 'skafferi-id_939', 'mejeri--ost---agg-id_256', 'frukt---gront-id_627']

    for ids in cat_ids:
        id_list = get_ids((ids,))
        prod_list = []
        while(len(id_list) > 0):
            if (len(id_list) > 10):
                min_list = []
                for i in range(0, 9):
                    min_list.append(id_list.pop())
                prod_list.extend(get_products(min_list))
            else:
                prod_list.extend(get_products(id_list))
                break
        write_csv(ids + ".csv", prod_list)

def get_ids(cat_id):
    id_url = 'https://handla.ica.se/api/content/v1/collections/facets/customer-type/B2C/store/maxi-ica-stormarknad-stenhagen-id_09699/products?categories=%s&bb=true'
    obj = json.loads(requests.get(id_url % cat_id).text)
    all_ids = []
    for product in obj['items']:
        all_ids.append(product['id'])
    return all_ids

def get_products(ids):
    products_url = 'https://handla.ica.se/api/content/v1/collections/customer-type/B2C/store/maxi-ica-stormarknad-stenhagen-id_09699/products?productIds='

    product_list = []
    
    line = ",".join(ids)
    print(products_url+line)
    prods = requests.get(products_url+line).text
    obj = json.loads(prods)
    
    for pr in obj:
        product = pr['product']
        price = pr['price']
    
        name = product['name']
        if 'originCountryCode' in product:
            origin_country = product['originCountryCode']['code']
        else:
            origin_country = 'unknown'
        if 'nutritionalInfo' in product:
            nutrition_value = parse_nutrition(product['nutritionalInfo'])
        else:
            nutrition_value = (0.0, 0.0, 0.0, 0.0)
    
        if 'comparePrice' in price:
            compare_price = price['comparePrice']
        elif 'listPrice' in price:
            compare_price = price['listPrice']
        else:
            compare_price = 0
        if 'comparePriceCode' in price:
            compare_price_type = price['comparePriceCode']
        else:
            compare_price_type = 'no'
        
        product_list.append(product_item(
            name, 
            origin_country, 
            nutrition_value,
            compare_price,
            compare_price_type
            )
        )

    return product_list
    

get_all()
