from fastapi import APIRouter, Depends  # routing and dependency injection
from sqlalchemy.orm import Session  # database session
from database import get_db  # database helper
import requests  # to make HTTP requests to SerpAPI
import os  # to read environment variables
from dotenv import load_dotenv  # to load .env file

load_dotenv()  # load the .env file so we can read SERPAPI_KEY

router = APIRouter()  # create shopping router

@router.get("/shopping")  # GET /shopping?product=iphone15
def search_product(product: str, db: Session = Depends(get_db)):  # product comes from URL query

    api_key = os.getenv("SERPAPI_KEY")  # get API key from .env file

    # Call SerpAPI Google Shopping search
    response = requests.get(
        "https://serpapi.com/search",  # SerpAPI endpoint
        params={
            "engine": "google_shopping",  # use Google Shopping engine
            "q": product,  # product to search
            "api_key": api_key,  # our API key
            "gl": "in",  # country = India
            "hl": "en"  # language = English
        }
    )

    data = response.json()  # convert response to dictionary

    # Extract shopping results
    results = data.get("shopping_results", [])  # get list of products, empty list if none

    if not results:  # if no results found
        return {"message": "No results found", "products": []}

    # Format top 5 results
    products = []  # empty list to store formatted products
    for item in results[:5]:  # only take first 5 results
        products.append({
            "title": item.get("title", ""),  # product name
            "price": item.get("price", "N/A"),  # product price
            "source": item.get("source", ""),  # store name e.g. Amazon, Flipkart
            "link": item.get("link", ""),  # link to product page
            "thumbnail": item.get("thumbnail", "")  # product image
        })

    # Find cheapest product
    cheapest = min(
        products,  # from all products
        key=lambda x: float(x["price"].replace("₹", "").replace(",", "").strip())
        if x["price"] != "N/A" else float("inf")  # ignore products with no price
    )

    # Buy now or wait logic
    # Simple rule - if cheapest price is reasonable, buy now
    buy_recommendation = "buy_now"  # default recommendation
    reason = "Good prices available right now"  # default reason

    # Check if all prices are similar (within 10% of each other)
    prices = []
    for p in products:
        if p["price"] != "N/A":
            try:
                price_num = float(p["price"].replace("₹", "").replace(",", "").strip())
                prices.append(price_num)
            except:
                pass

    if prices:
        min_price = min(prices)  # lowest price
        max_price = max(prices)  # highest price
        price_difference = max_price - min_price  # difference between highest and lowest

        if price_difference > min_price * 0.2:  # if prices vary by more than 20%
            buy_recommendation = "compare_more"  # suggest comparing more
            reason = f"Prices vary a lot (₹{min_price:.0f} to ₹{max_price:.0f}). Compare carefully before buying."
        else:
            buy_recommendation = "buy_now"
            reason = f"Prices are consistent around ₹{min_price:.0f}. Good time to buy."

    return {
        "product_searched": product,  # what user searched for
        "total_results": len(products),  # how many results found
        "cheapest": cheapest,  # cheapest option
        "recommendation": buy_recommendation,  # buy now or compare more
        "reason": reason,  # why we recommend this
        "all_products": products  # all products found
    }