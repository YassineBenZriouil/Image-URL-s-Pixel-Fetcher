# Image-URL-s-Pixel-Fetcher
A Python script to fetch image URLs for any entity (not just animals) and update a JSON file with the fetched data. The script ensures that missing image URLs are populated based on the entity name via the Pexels API.

## Features

- Fetches a single image for each entity in the dataset.
- Processes entities without image URLs and updates them.
- Supports batch processing: you can process a specified number of entities at a time.
- Handles API rate-limiting by adding a delay between requests.
- Automatically saves the updated JSON file.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/your-username/ImageFetcher.git

cd Image-URL-s-Pixel-Fetcher

pip install requests
