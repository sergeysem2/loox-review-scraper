import requests
import csv
import time
import os
from urllib.parse import urlparse

store_name = "eric-box"
encoded_product_id = "Z2lkOi8vc2hvcGlmeS9Qcm9kdWN0LzY5MzAwODcyNjA0MjI="  # Replace if needed
max_pages = 10
output_csv = "reviews.csv"
image_folder = "review_images"

headers = {
    "User-Agent": "Mozilla/5.0"
}

# Create image folder if it doesn't exist
os.makedirs(image_folder, exist_ok=True)

# CSV Setup
with open(output_csv, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Reviewer Name", "Rating", "Review Text", "Date", "Image Filenames"])

    for page in range(1, max_pages + 1):
        url = f"https://loox.io/widget/YUtV5p1gqJ/reviews/9249279541525?limit=100&page={page}"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Failed on page {page} with status code {response.status_code}")
            break

        data = response.json()
        reviews = data.get("reviews", [])

        if not reviews:
            print(f"No more reviews found on page {page}.")
            break

        for idx, review in enumerate(reviews):
            photos = review.get("photos", [])
            image_filenames = []

            for i, photo_url in enumerate(photos):
                try:
                    parsed_url = urlparse(photo_url)
                    file_name = os.path.basename(parsed_url.path)
                    image_path = os.path.join(image_folder, file_name)

                    img_data = requests.get(photo_url).content
                    with open(image_path, "wb") as img_file:
                        img_file.write(img_data)

                    image_filenames.append(file_name)
                except Exception as e:
                    print(f"Failed to download image: {photo_url} - {e}")

            writer.writerow([
                review.get("reviewer_name", ""),
                review.get("rating", ""),
                review.get("text", "").replace("\n", " "),
                review.get("created", ""),
                ", ".join(image_filenames)
            ])

        print(f"✅ Page {page} processed with {len(reviews)} reviews.")
        time.sleep(1)  
