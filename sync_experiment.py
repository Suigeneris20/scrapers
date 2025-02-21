import time
import json
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=False)
    context = browser.new_context(viewport={"width": 1920, "height": 1080})
    page = context.new_page()

    # go to url
    page.goto("https://wearpact.com/men/apparel")  # go to url
    page.wait_for_selector('.product-link', timeout=30000)  # wait for content to load

    parsed = []
    product_links = page.locator('.product-link').all()
    for prod in product_links:
        parsed.append({
            #"title": box.query_selector("h3").inner_text(),
            "url": prod.get_attribute("href"),
            # tags are not always present:
            #"tags": box.query_selector(".tw-tag").inner_text() if box.query_selector(".tw-tag") else None,
        })
    #next_button = page.locator("//a[contains(@class, 'paginate')]").get_attribute("href")
    #print(next_button)
    results = []
    print(parsed)
    for item in parsed:
        #print(video)
        
        link = item['url']
        link = f'https://wearpact.com{link}'
        #print(link)
        page.goto(link)

        images = page.locator('#product-images-wrapper img').all()

        image_sources = set()
        for img in images:
            src = img.get_attribute("src")
            if src and src.startswith("//"):
                src = "https:" + src  # Convert relative URLs to absolute
            image_sources.add(src)

        lis_img = list(image_sources)
        print(len(lis_img))
        print(lis_img)

   

        #element = page.query_selector(".product__section-details__inner--product_description .rte")
        #print(element.inner_text())
        #print(page)
        #page.wait_for_selector('.product-information-features ul', timeout=30000)
        
        
        '''
        # Extract the `src` attribute from images
        img_elements = page.query_selector_all("#slider img")
        img_urls = [img.get_attribute("src") for img in img_elements if img_elements]
        '''

            #result.append(f"{t} {value} {unit} {description}")

            #results.append(result)
    print(img_urls)
