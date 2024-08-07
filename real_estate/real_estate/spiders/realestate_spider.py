import scrapy

class MySpider(scrapy.Spider):
    name = "edgeprop"
    start_urls = ['https://www.edgeprop.my/buy/malaysia/all-residential']

    def parse(self, response):
        # Find the pagination element
        pagination = response.css('li.page-item')
        if pagination:
            # Find the list of page numbers
            page_numbers = pagination.css('a.page-link::text').getall()

            # Convert page numbers to integers
            page_numbers = [int(num) for num in page_numbers if num.isdigit()]

            # Find the maximum page number
            max_page = max(page_numbers)

            # Output the maximum page number
            print("Maximum page number:", max_page)
        else:
            print("Pagination element not found.")

# class PropertyHunterSpider(scrapy.Spider):
#     name = 'propertyhunter_spider'
#     start_urls = ['https://www.propertyhunter.com.my/sale/search/petaling-jaya']

#     def parse(self, response):
#         # Extract property listings
#         listings = response.css('div.listing-box')

#         for listing in listings:
#             # Extract listing details
#             title = listing.css('p.listing-name::text').get()
#             price = listing.css('span.listing-price::text').get()
#             location = listing.css('p.listing-location::text').get()

#             title = title.strip()
#             location = location.strip()
#             price = price.strip()

#             item = PropertyItem()
#             item['title'] = title
#             item['price'] = price
#             item['location'] = location

#             yield item

        # Follow pagination links
        # next_page_url = response.css('.next a::attr(href)').get()
        # if next_page_url:
        #     yield response.follow(next_page_url, self.parse)

        

# class MySpider(scrapy.Spider):
#     name = 'my_spider'

#     def start_requests(self):
#         # Define the raw TML strings to process
#         html_strings = '''
#            
#             '''
#             # Add more HTML strings as needed
        

#      response = HtmlResponse(url='dummy_url', body=html_string, encoding='utf-8')

#         yield scrapy.Request(url='', meta={'response': response}, callback=self.parse)


#     def parse(self, response):
#         # Extract content from the HTML response
#         selector = Selector(response=response)
#         title = selector.css('h3.listing-name::text').get()
#         # price = response.css('p::text').get()
#         # location = response.css('p::text').get()

#         # Process the extracted data as needed
#         # ...

#         yield {
#             'title': title,
#             # 'paragraph': paragraph,
#         }

