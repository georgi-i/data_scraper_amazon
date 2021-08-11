from selenium import webdriver
import pandas as pd
from time import sleep
from re import match
from pyfiglet import figlet_format


welcome = figlet_format("Hello", font = "isometric1")
print(welcome)

domain = input('Choose between USA, DE, FR, ES, IT or UK for the scraping: ')
if domain == 'USA':
    domain = 'https://www.amazon.com'
elif domain == 'DE':
    domain = 'https://www.amazon.de'    
elif domain == 'FR':
    domain = 'https://www.amazon.fr'
elif domain == 'ES':
    domain = 'https://www.amazon.es'
elif domain == 'IT':
    domain = 'https://www.amazon.it'
elif domain == 'UK':
    domain = 'https://www.amazon.co.uk'


def scrape_data(driver, selector):
    data = driver.find_elements_by_css_selector(selector)
    lines = []
    for line in data:
        lines.append(line.text)
    return lines

def scrape_authors_and_date():
    author_and_date_css = 'div.sg-col-inner div.a-section.a-spacing-none h2.a-size-mini.a-spacing-none.a-color-base.s-line-clamp-2 +*'
    authors = []
    dates = []
    data = scrape_data(driver, author_and_date_css)
    for line in data:
        r = r'by\s*([A-Za-z\s\.,]+)'
        try:
            author = match(r, line).group(0)
        except:
            author = float('nan')
        try:
            date = line.split('|')[-1]
            if '|' not in line:
                date = float('nan')
        except:
            date = float('nan')
        
        authors.append(author)
        dates.append(date)
    
    return [authors, dates]

def scrape_rating_and_reviews(driver):
    rr_selector = 'div.s-include-content-margin.s-border-bottom.s-latency-cf-section div.a-section.a-spacing-none.a-spacing-top-micro span[aria-label]'
    rating = []
    reviews = []
    data = driver.find_elements_by_css_selector(rr_selector)
    swap = False
    for line in data:
        current_element = line.get_attribute('aria-label')
        if current_element[0].isdigit():
            if not swap:
                try:
                    current_rating = float(current_element.split()[0])
                except:
                    current_rating = 0
                rating.append(current_rating)
                swap = True
            elif swap:
                try:
                   current_reviews = float(current_element.replace(',', ''))
                except:
                    current_reviews = 0
                reviews.append(current_reviews)
                swap = False
    
    return [rating, reviews]
        
def scrape_prices(driver):
    css_selector_price = r'div[data-component-type="s-search-result"] div.a-row.a-size-base.a-color-base:nth-child(2) span[data-a-size="l"]>span:first-of-type'
    data = driver.find_elements_by_css_selector(css_selector_price)
    prices = [0] * len(data)
    for i in range(len(data)):
        try:
            price = float(data[i].get_attribute("textContent").strip('$'))
        except:
            price = 0
        prices[i] = price
    
    return prices

def scrape_asin(driver):
    css_asin = r'div[data-component-type="s-search-result"] div.a-section.a-spacing-none h2 a'
    data = driver.find_elements_by_css_selector(css_asin)
    asins = []
    for line in data:
        try:
            asin = line.get_attribute('href').split('/')[5]
        except:
            asin = None

        asins.append(asin)
    
    return asins


def scrape_urls(driver, domain):
    
    css_urls = r'div[data-component-type="s-search-result"] h2 a.a-link-normal.a-text-normal[href]'
    data = driver.find_elements_by_css_selector(css_urls)
    urls = []
    for line in data:
        try:
            url = line.get_attribute('href')
            urls.append(url)
        except:
            continue

    return urls


def load_url(driver, keyword, domain):
    url = f'{domain}/s?k={keyword}'
    driver.get(url)
    #sleep(2.5)

def calc_results_value(results_for_keyword, values):
    if results_for_keyword > 10000:
        values['results'] = 1
    elif 4001 <= results_for_keyword <= 10000:
        values['results'] = 2
    elif 2501 <= results_for_keyword <= 4000:
        values['results'] = 3
    elif 1001 <= results_for_keyword <= 2500:
        values['results'] = 4
    elif 501 <= results_for_keyword <= 1000:
        values['results'] = 5
    elif 76 <= results_for_keyword <= 500:
        values['results'] = 6
    elif 0 <= results_for_keyword <= 75:
        values['results'] = 7
    
    return values

def calc_reviews_value(average_reviews, values):
    if average_reviews >= 1000:
        values['average_reviews'] = 1
    elif 500 <= average_reviews <= 999:
        values['average_reviews'] = 2
    elif 350 <= average_reviews <= 499:
        values['average_reviews'] = 3
    elif 100 <= average_reviews <= 349:
        values['average_reviews'] = 4
    elif 50 <= average_reviews <= 99:
        values['average_reviews'] = 5
    elif 25 <= average_reviews <= 49:
        values['average_reviews'] = 6
    elif 0 <= average_reviews <= 24:
        values['average_reviews'] = 7
    
    return values

def calc_price_value(average_price, values):
    if 0 <= average_price <= 5:
        values['average_price'] = 1
    elif 5 < average_price <= 6:
        values['average_price'] = 2
    elif 6 < average_price <= 7:
        values['average_price'] = 3
    elif 7 < average_price <= 8:
        values['average_price'] = 4
    elif 8 < average_price <= 9:
        values['average_price'] = 5
    elif 9 < average_price <= 10:
        values['average_price'] = 6
    elif 10 <= average_price:
        values['average_price'] = 7
    
    return values

def calc_rating_value(average_rating, values):
    if 0 <= average_rating <= 0.04:
        values['average_rating'] = 1
    elif 4.8 <= average_rating <= 5:
        values['average_rating'] = 2
    elif 4.3 <= average_rating <= 4.7:
        values['average_rating'] = 3
    elif 3.8 <= average_rating <= 4.2:
        values['average_rating'] = 4
    elif 3.4 <= average_rating <= 3.7:
        values['average_rating'] = 5
    elif 2.8 <= average_rating <= 3.3:
        values['average_rating'] = 6
    elif 0.5 <= average_rating <= 2.7:
        values['average_rating'] = 7
    
    return values

#executable_path=r'/set/the/path/to/chromedriver'
driver = webdriver.Chrome()    

keywords = None
with open('keywords.txt', 'r') as f:
    keywords = f.readlines()


for keyword in keywords:

    load_url(driver, keyword, domain)
    sleep(2.5)

    print('Scraping...')
    css_selector_title = r'div[data-component-type="s-search-result"] h2 a.a-link-normal.a-text-normal'
    titles = scrape_data(driver, css_selector_title)
    authors_and_date = scrape_authors_and_date()
    rating_and_reviews = scrape_rating_and_reviews(driver)
    prices = scrape_prices(driver)
    css_selector_cover = r'div[data-component-type="s-search-result"] div.a-section.a-spacing-none.a-spacing-top-small div.a-row.a-size-base.a-color-base a.a-size-base.a-link-normal.a-text-bold'
    covers = scrape_data(driver, css_selector_cover)
    asins = scrape_asin(driver)
    total_results = scrape_data(driver, 'div.sg-col-inner div.a-section.a-spacing-small.a-spacing-top-small>span:nth-child(1)')[0]
    urls = scrape_urls(driver, domain)


    for i in range(len(asins)):
        if i >= len(asins):
            break
        if 'Redirect' in asins[i]:
            asins.pop(i)
            titles.pop(i)

    average_rating = float(f'{(sum(rating_and_reviews[0]) / len(rating_and_reviews[0])):.1f}')
    average_reviews = float(f'{(sum(rating_and_reviews[1]) / len(rating_and_reviews[1])):.1f}')
    average_price = float(f'{(sum(prices) / len(prices)):.1f}')
    paperback_books = f'      {covers.count("Paperback")}/{len(covers)}'
    try:
        results_for_keyword = float(total_results.split()[3].replace(',',''))
    except:
        results_for_keyword = float(total_results.split()[2].replace(',',''))

    importance_values = {'results': 4, 'average_reviews': 3, 'average_price': 3, 'average_rating': 3}

    total_score_values = {}

    total_score_values = calc_results_value(results_for_keyword, total_score_values)
    total_score_values = calc_reviews_value(average_reviews, total_score_values)
    total_score_values = calc_price_value(average_price, total_score_values)
    total_score_values = calc_rating_value(average_rating, total_score_values)

    total_score = 0
    for key in importance_values:
        total_score += importance_values[key] * total_score_values[key]

    total_score_percentage = f'{((total_score / 119) * 100):.2f}%'


    # First dataframe to xlsx
    keyword = keyword.replace(' ', '_').strip('\n')
    print(f'Writing result to result_{keyword}.xlsx')

    results = total_results.split()
    page_1_results = '     ' + results[0]
    results_quantity = '     ' + results[3].replace(',', '')

    val_dict_1 = {'Keyword Searched - USA, DE, FR, ES, IT, UK': keyword, 
                'Score:': int(total_score), 
                'Results on Page 1': page_1_results, 
                'Total Results': results_quantity,
                'Average Review Rating': average_rating, 
                'Average Total Reviews': average_reviews,
                'Average Price': average_price,
                'Paperback VS All Types': paperback_books
                }
    
    df_1 = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in val_dict_1.items() ]))

    
    writer = pd.ExcelWriter(f'result_{keyword}.xlsx', engine='xlsxwriter')

    df_1.to_excel(writer, sheet_name='Keywords Overview', index=False)

    worksheet_1 = writer.sheets['Keywords Overview']

    worksheet_1.set_column('A:A', 40)
    worksheet_1.set_column('B:B', 25)
    worksheet_1.set_column('C:C', 30)
    worksheet_1.set_column('D:D', 30)
    worksheet_1.set_column('E:E', 25)
    worksheet_1.set_column('F:F', 25)
    worksheet_1.set_column('G:G', 35)
    worksheet_1.set_column('H:H', 35)
    worksheet_1.set_column('I:I', 25)

    # Second dataframe to xlsx
    keyword_list = [keyword] * len(titles)


    val_dict_2 = {'Keyword Searched to Find Result': keyword_list, 
                'Title': titles, 
                'ASIN': asins, 
                'Author Name': authors_and_date[0],
                'Review Rating': rating_and_reviews[0], 
                'Total Reviews': rating_and_reviews[1],
                'Price of Book': prices,
                'Date Published': authors_and_date[1],
                'Type of Book': covers,
                'Product Page URL': urls
                }

    df_2 = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in val_dict_2.items() ]))
    styled_df_2 = df_2.style.highlight_max(subset=['Review Rating', 'Total Reviews', 'Price of Book'], color='#90ee90').highlight_min(subset=['Review Rating', 'Total Reviews', 'Price of Book'], color='#cd4f39')

    styled_df_2.to_excel(writer, sheet_name='ASINS, Authors, Titles & More', index=False)
    worksheet_2 = writer.sheets['ASINS, Authors, Titles & More']

    worksheet_2.set_column('A:A', 30)
    worksheet_2.set_column('B:B', 105)
    worksheet_2.set_column('C:C', 35)
    worksheet_2.set_column('D:D', 25)
    worksheet_2.set_column('E:E', 25)
    worksheet_2.set_column('F:F', 20)
    worksheet_2.set_column('G:G', 25)
    worksheet_2.set_column('H:H', 25)
    worksheet_2.set_column('I:I', 25)
    worksheet_2.set_column('J:J', 75)
    writer.save()

    print('Sleep for 5 sec before next scraping...')
    sleep(5)


driver.quit()


