
import time
from bs4 import BeautifulSoup
import requests
import pandas as pd

payload = {
    'source': 'universal',
    'url': 'https://www.propertyguru.com.my/property-for-sale',
}

response = requests.post(
    'https://realtime.oxylabs.io/v1/queries',
    json = payload,
    auth=('demouser', '!234Demouser'),
)

responseJson = response.json()['results']
html_content = responseJson[0]['content']

html_content_cleaned = html_content.replace('\\', '')
soup = BeautifulSoup(html_content_cleaned, 'html.parser')
elements = soup.find_all(class_='listing-card')
data = []

#value transaction
brickz_payload = {
    'source': 'universal',
    'url': 'https://www.brickz.my/transactions/residential',
}

brickz_response = requests.post(
    'https://realtime.oxylabs.io/v1/queries',
    json = brickz_payload,
    auth=('demouser', '!234Demouser'),
)

brickz_responseJson = brickz_response.json()['results']
brickz_html_content = brickz_responseJson[0]['content']
brickz_html_content_cleaned = brickz_html_content.replace('\\', '')
brickz_soup = BeautifulSoup(brickz_html_content_cleaned, 'html.parser')
brickz_elements = brickz_soup.find_all(lambda tag: tag.has_attr('itemtype') and tag['itemtype'] == 'https://schema.org/AdministrativeArea')

#loop for all pages
page_numbers = brickz_soup.find_all(class_="page-numbers")
page_numbers_list = []

if page_numbers:
    for page in page_numbers:
        if page.get_text().isdigit():
            page_numbers_list.append(page.get_text())
    max_page = int(max(page_numbers_list))
    min_page = int(min(page_numbers_list))
    current_page = min_page
    while max_page > current_page:
        next_page = str(current_page + 1)
        brickz_detail_payload = {
            'source': 'universal',
            'url': 'https://www.brickz.my/transactions/residential/page/' + next_page,
        }
        brickz_detail_response = requests.post(
            'https://realtime.oxylabs.io/v1/queries',
            json = brickz_detail_payload,
            auth=('demouser', '!234Demouser'),
        )
        brickz_detail_html_content = brickz_detail_response.json()['results']
        brickz_detail_html_content_cleaned = brickz_html_content.replace('\\', '')
        brickz_detail_soup = BeautifulSoup(brickz_detail_html_content_cleaned, 'html.parser')
        brickz_detail_elements = brickz_detail_soup.find_all(lambda tag: tag.has_attr('itemtype') and tag['itemtype'] == 'https://schema.org/AdministrativeArea')
        brickz_elements.extend(brickz_detail_elements)
        current_page += 1
else:
    print("No page numbers found.")


for item in elements:
    name = item.find('a', class_='nav-link').get_text()
    price = item.find('span', class_='price').get_text()
    price_range = ""

    if price: 
        price = price.split(" - ")[-1] if " - " in price else price

        char_remov = [',', 'RM']
        for char in char_remov:
            # replace() "returns" an altered string
            price = price.replace(char, "")
        
        if "." in price:
            price = float(price)
        elif not price.isdigit():
            price = 0
        else:
            price = int(price)
        
        if price < 300000:
            price_range = "< RM300k"
        elif price >= 300000 and price <= 600000:
            price_range = "RM300k - RM600k"
        elif price > 600000 and price <= 1000000:
            price_range = "RM600k - RM1M"
        elif price > 1000000 and price <= 1500000:
            price_range = "RM1M - RM1.5M"
        elif price > 1500000:
            price_range = "> RM1.5M"

    # address
    tag_property = 'itemprop'
    target_property_value = 'streetAddress'
    target_tag = item.find(lambda tag: tag.has_attr(tag_property) and tag[tag_property] == target_property_value)

    address = target_tag.get_text().split(', ')
    state = address[len(address) - 1]
    district = address[len(address) - 2]

    detail_url = item.find('a', class_='nav-link').get('href')
    detail_payload = {
        'source': 'universal',
        'url': detail_url,
    }

    detail_response = requests.post(
        'https://realtime.oxylabs.io/v1/queries',
        json = detail_payload,
        auth=('demouser', '!234Demouser'),
    )
    detail_responseJson = detail_response.json()['results']
    detail_html_content = detail_responseJson[0]['content']
    detail_html_content_cleaned = detail_html_content.replace('\\', '')
    detail_soup = BeautifulSoup(detail_html_content_cleaned, 'html.parser')

    built_year_element = detail_soup.find('tr', class_='completion-year')

    if built_year_element:
        built_year = built_year_element.find('td', class_='value-block').get_text()
        arr_build_year = []
        if ", " in built_year:
            arr_build_year = built_year.split(', ')
            year = arr_build_year[len(arr_build_year) - 1]
        else: 
            year = built_year
        
        #get half year and quarter year
        quarter_year = built_year
        half_year = built_year

        if len(arr_build_year) > 1:
            match arr_build_year[0]:
                case "January" | "February" | "March":
                    quarter_year = f"Q1 {year}"
                    half_year = f"H1 {year}"      
                case "April" | "May" | "June":
                    quarter_year = f"Q3 {year}"
                    half_year = f"H1 {year}"
                case "July" | "August" | "September":
                    quarter_year = f"Q3 {year}"
                    half_year = f"H2 {year}"
                case "October" | "November" | "December":
                    quarter_year = f"Q4 {year}"
                    half_year = f"H2 {year}" 
                case _:
                    quarter_year = year
                    half_year = year
    else: 
        year = ""
        half_year = ""
        quarter_year = ""

    property_type_element = detail_soup.find('tr', class_='property-type')

    if property_type_element:
        property_type = property_type_element.find('td', class_='value-block').get_text()        
    else: 
        property_type = ""

    value_transaction = 0
    number_transaction = 0
    if brickz_elements is not None:
        for property in brickz_elements:
            if property.find('a', class_='ptd_list_item_title').get_text() == name.upper():
                total_number_transaction = property.find('a', class_='button').get_text()
                number_transaction = ''.join(filter(str.isdigit, total_number_transaction))
                median_total_transaction = int(property.find('span', class_='ptd_currency').get_text())
                value_transaction = median_total_transaction * int(number_transaction)

    data.append([name , state, district, year, half_year, quarter_year, property_type, price, value_transaction, number_transaction])

print("finishing...")
current_timestamp = time.time()
df = pd.DataFrame(data, columns=['Name', 'State', 'District', 'Year', 'Half Year', 'Quarter', 'Prototype', 'Price Range', 'Value Transaction', 'Number Transaction'])
df.to_excel(f"{current_timestamp}.xlsx", index=False)
print("DONE!")