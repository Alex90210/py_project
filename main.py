import sys
import requests
from bs4 import BeautifulSoup
import json

def fetch_product_info(product_name):
    search_term = product_name.replace(' ', '+')
    search_url = f"https://www.compari.ro/CategorySearch.php?st={search_term}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    product_boxes = soup.find_all('div', class_='product-box')
    if not product_boxes:
        print(f"No results found for '{product_name}'")
        return None

    first_product = product_boxes[0]
    name_tag = first_product.find('h2')
    if name_tag:
        product_name = name_tag.get_text(strip=True)
    else:
        product_name = "Unknown Product"

    product_link_tag = name_tag.find('a') if name_tag else None
    if product_link_tag:
        product_link = product_link_tag['href']
    else:
        print(f"Could not find product link for '{product_name}'")
        return None

    product_page_url = product_link
    if not product_page_url.startswith('http'):
        product_page_url = 'https://www.compari.ro' + product_page_url

    product_response = requests.get(product_page_url, headers=headers)
    product_soup = BeautifulSoup(product_response.content, 'html.parser')

    # Find all offer containers
    offers = product_soup.find_all('div', class_='optoffer')

    prices = []
    for offer in offers:
        price_span = offer.find('span', itemprop='price')
        if price_span:
            price_value = price_span.get('content')
            if price_value and price_value.replace('.', '', 1).isdigit():
                prices.append(float(price_value))
                print(f"Extracted price: {price_value}")
            else:
                price_text = price_span.get_text(strip=True).replace('RON', '').replace(',', '').replace(' ', '')
                price_value = ''.join(filter(lambda x: x.isdigit() or x == '.', price_text))
                if price_value:
                    prices.append(float(price_value))
                    print(f"Extracted price: {price_value}")

    if prices:
        best_price = min(prices)
        highest_price = max(prices)
    else:
        best_price = None
        highest_price = None

    offers_tag = first_product.find('a', class_='offer-num')
    if offers_tag:
        offers_text = offers_tag.get_text(strip=True)
        num_offers = ''.join(filter(str.isdigit, offers_text))
    else:
        num_offers = None

    product_info = {
        'product_name': product_name,
        'best_price': str(best_price) if best_price else None,
        'highest_price': str(highest_price) if highest_price else None,
        'num_offers': num_offers
    }

    return product_info

def main():
    if len(sys.argv) < 2:
        print('Usage: python main.py "product 1" "product 2"')
        sys.exit(1)

    product_names = sys.argv[1:]
    products_info = []

    for product_name in product_names:
        print(f"\nProcessing product: {product_name}")
        info = fetch_product_info(product_name)
        if info:
            products_info.append(info)

    with open('product_prices.json', 'w', encoding='utf-8') as f:
        json.dump(products_info, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()