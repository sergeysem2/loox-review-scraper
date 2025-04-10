from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import csv
import os
import time
import requests
from urllib.parse import urlparse

# === CONFIG ===
product_url = "https://www.eric-box.com/products/ee-shorts"
output_csv = "reviews.csv"
image_folder = "review_images"

# Setup Selenium with headless Chrome using webdriver-manager
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920x1080')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Create output folder for images
os.makedirs(image_folder, exist_ok=True)

# Open CSV for writing
with open(output_csv, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Reviewer Name", "Rating", "Review Text", "Date", "Image Filenames"])

    print(f"🌐 Opening product page: {product_url}")
    driver.get(product_url)
    wait = WebDriverWait(driver, 10)

    # Scroll down to the reviews section
    time.sleep(5)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)

    # Continuously click 'Load More' until all reviews are shown
    while True:
        try:
            load_more = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Load More')]")))
            driver.execute_script("arguments[0].click();", load_more)
            time.sleep(3)
        except:
            print("✅ All reviews loaded or no 'Load More' button found.")
            break

    # Parse review elements
    reviews = driver.find_elements(By.CSS_SELECTOR, ".loox-review")
    print(f"📝 Found {len(reviews)} reviews")

    total_reviews = 0

    for review in reviews:
        try:
            reviewer_name = review.find_element(By.CSS_SELECTOR, ".loox-author-name").text
            rating = len(review.find_elements(By.CSS_SELECTOR, ".loox-star.loox-filled"))
            review_text = review.find_element(By.CSS_SELECTOR, ".loox-review-content").text
            date = review.find_element(By.CSS_SELECTOR, ".loox-review-date").text

            photos = review.find_elements(By.CSS_SELECTOR, ".loox-gallery-image")
            image_filenames = []

            for photo in photos:
                try:
                    photo_url = photo.get_attribute("src")
                    file_name = os.path.basename(urlparse(photo_url).path)
                    image_path = os.path.join(image_folder, file_name)

                    img_data = requests.get(photo_url).content
                    with open(image_path, "wb") as img_file:
                        img_file.write(img_data)

                    image_filenames.append(file_name)
                except Exception as e:
                    print(f"❌ Failed to download image: {photo_url} — {e}")

            writer.writerow([reviewer_name, rating, review_text.replace("\n", " "), date, ", ".join(image_filenames)])
            total_reviews += 1

        except Exception as e:
            print(f"⚠️ Skipped a review due to error: {e}")

    driver.quit()
    print(f"\n🎉 Scraping complete! Total reviews saved: {total_reviews}")
    print(f"📄 Output CSV: {output_csv}")
    print(f"🖼️ Images saved to: {image_folder}/")
    print("🔄 Closing browser...")