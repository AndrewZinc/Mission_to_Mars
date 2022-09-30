# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt


def scrape_all():
    # Initiate headless mode for scraping
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)
    news_title, news_paragraph = mars_news(browser)
    
    # Run all the scraping functions and store the results in a dictionary
    data = {
        'news_title': news_title,
        'news_paragraph': news_paragraph,
        'featured_image': featured_image(browser),
        'facts': mars_facts(),
        'hemispheres': hemispheres(browser),
        'last_modified': dt.datetime.now()
    }
    # stop webdriver and return the data
    browser.quit()
    return data


def mars_news(browser):
    # Visit the NASA Mars News website
    url = 'https://redplanetscience.com/'
    browser.visit(url)

    # Optional delay for page loading
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert browser HTML to a BeautifulSoup object
    html = browser.html
    news_soup = soup(html, 'html.parser')
    
    # Add Try-except for error-handling
    try:
        slide_elem = news_soup.select_one('div.list_text')

        # Use the parent element to find the first 'a' tag and save it as 'news_title
        news_title = slide_elem.find('div', class_='content_title').get_text()

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    except AttributeError:
        return None, None
    
    return news_title, news_p

# ### Featured Images

def featured_image(browser):
    # Visitation URL
    url = 'https://spaceimages-mars.com/'
    browser.visit(url)

    # Find and click the Full Image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting HTML with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add Try-except for error-handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
    except AttributeError:
        return None
    
    # Use the base URL to create an absolute URL
    img_url = (f'https://spaceimages-mars.com/{img_url_rel}')
    
    return img_url


def mars_facts():
    
    # Add try-except for error-handling
    try:
        df = pd.read_html('https://galaxyfacts-mars.com/')[0]
    except BaseException:
        return None
    
    df.columns = ['description', 'Mars', 'Earth']
    df.set_index('description', inplace=True)
    return df.to_html(classes="table table-striped")


def hemispheres(browser):
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    # Create a list to hold the images and titles.
    hemisphere_image_urls = []
    pages = []
    # Write code to retrieve the image urls and titles for each hemisphere.
    html = browser.html
    hemi_soup = soup(html, 'html.parser')

    # find the links to the product pages
    results = hemi_soup.find('div', class_='collapsible results')

    for link in results.find_all('a'):
        page = link.get('href')
        
        if page in pages:
            pass
        else:
            pages.append(page)

    # Loop through the product pages to get the image urls and titles.      

    for page in pages:
        img_page = url + page
        browser.visit(img_page)
        
        img_temp_soup = soup(browser.html, 'html.parser')
        try: 
            # get the image href
            href = img_temp_soup.li.find('a', target='_blank').get('href')
            
            # get the image title
            title = img_temp_soup.h2.get_text()

            # Store the image title and the full url in a dictionary
            data = {"img_url": url + href, "title": title}
            hemisphere_image_urls.append(data)
        except BaseException:
            return None

    # Print the list that holds the dictionary of each image url and title.
    return hemisphere_image_urls

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())