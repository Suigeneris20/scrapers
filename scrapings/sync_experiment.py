import time
import json
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=False)
    context = browser.new_context(viewport={"width": 1920, "height": 1080})
    page = context.new_page()

    # go to url
    base_url = "https://www.outerknown.com/collections/mens-new-arrivals?"
    #page_number = 1
    links = []

    url = base_url
    page.goto(url)
    
    try:
        while True:
            

            # Optional: Scroll to the bottom to trigger dynamic loading
            #page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2000)  # Small delay for content to appear

            #page.wait_for_selector('.product-group-card a', timeout=30000)  # wait for content to load

            anchor_tags = page.locator('.product-group-card a').all()
            for anchor in anchor_tags:
                href = anchor.get_attribute("href")
                if href and not href.startswith("Javascript:"):  # Ignore JavaScript links
                    if href.startswith("/"):  
                        href = "https://www.tentree.com" + href  # Convert relative URLs to absolute
                        links.append(href)

            load_more = page.locator("button.load-more-btn")
            if load_more.count() > 0:
                print("Clicking 'Load More' button...")
                load_more.click()
                page.wait_for_timeout(3000)
            
            else:
                break
    except Exception as e:
        print(f"Error occured while collecting product links")
    print("Finished collecting links")
    
    #print(links)

    product_details = {}

    for item in links:
        page.goto(item)
        try:
            product_details["description"] = page.locator("#meet-the-product-container p").inner_text().strip()

        except Exception as e:
            print(f"Not clothing item: {item}, hence: {e}")
        # Extract sustainability information
        sustainability_titles = ["Organic Cotton", "Made from recycled materials", "Fabric composition"]
        for title in sustainability_titles:
            try:
                section_locator = page.locator(f"//h4[contains(text(), '{title}')]/following-sibling::p")
                if section_locator.count() > 0:
                    product_details[title] = section_locator.first.inner_text().strip()
                else:
                    product_details[title] = "Not Found"
            except Exception:
                product_details[title] = "Not Found"

    print(product_details)
    '''
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

   '''

        #element = page.query_selector(".product__section-details__inner--product_description .rte")
        #print(element.inner_text())
        #print(page)
        #page.wait_for_selector('.product-information-features ul', timeout=30000)
        
        
        
        # Extract the `src` attribute from images
        #img_elements = page.query_selector_all("#slider img")
        #img_urls = [img.get_attribute("src") for img in img_elements if img_elements]
        

            #result.append(f"{t} {value} {unit} {description}")

            #results.append(result)
   # print(img_urls)
