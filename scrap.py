# Importing necessary libraries
import requests
from bs4 import BeautifulSoup

# URL of the webpage (replace with the actual URL of the page you're scraping)
url = 'https://onou.dz/gestion_stock/#/bons'  # Change this to your actual webpage URL

# Send a GET request to fetch the webpage content
response = requests.get(url)

# Check if the request was successful (status code 200 means OK)
if response.status_code == 200:
    # Parse the content of the page with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the table by class name (adjust the class name as per your table)
    # You can inspect the page to find the exact table class
    table = soup.find('table', {'class': 'table table-bordered table-hover'})  # Change class name if necessary

    # Define the target date for which you want to sum 'السعر الكلي'
    target_date = '2024-10-23'  # Example date, change as needed

    # Initialize a variable to hold the sum
    total_sum = 0

    # Check if the table exists
    if table:
        # Find all rows in the table except the header (which is the first row)
        rows = table.find_all('tr')[1:]  # Skipping the header row

        # Loop over the rows to process each row
        for row in rows:
            # Get all the cells (td elements) in the row
            cells = row.find_all('td')

            # Extract the date (from the third column - index 2, adjust if needed)
            date = cells[2].text.strip()

            # Check if the date matches the target date
            if date == target_date:
                # Extract the total price (from the fourth column - index 3, adjust if needed)
                price_str = cells[3].text.strip().replace(',', '')  # Remove commas for large numbers
                price = float(price_str)  # Convert the string to a float

                # Add the price to the running total
                total_sum += price

        # Print the final sum of 'السعر الكلي' for the target date
        print(f"Total sum of 'السعر الكلي' for {target_date}: {total_sum}")
    else:
        print("Table not found on the page.")
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")
