# SI 201 HW4 (Library Checkout System)
# Your name: Ryan Brenner
# Your student id: ryanbren
# Your email: ryanbren@umich.edu
# Who or what you worked with on this homework (including generative AI like ChatGPT):
# If you worked with generative AI also add a statement for how you used it.
# I used AI to help me debug and to better understand Soup/XML. Since I missed a lecture, I needed to use 
# ChatGPT to help me catch up and learn as I did the project. 

from bs4 import BeautifulSoup
import re
import os
import csv
import unittest
import requests  # kept for extra credit parity


# IMPORTANT NOTE:
"""
If you are getting "encoding errors" while trying to open, read, or write from a file, add the following argument to any of your open() functions:
    encoding="utf-8-sig"
"""


def load_listing_results(html_path) -> list[tuple]:
   
    results = []
    with open(html_path, "r", encoding="utf-8-sig") as file:
        soup = BeautifulSoup(file.read(), "html.parser")

        links = soup.find_all("a", href=True)

        for link in links:
            href = link["href"]

            if "/rooms/" in href: 
                listing_id = href.split("/rooms/")[1].split("?")[0].split("/")[-1]
                listing_title = link.find_next("div").get_text(" ", strip=True).split("Super Clean")[0].strip()
                if listing_title:
                    listing_tuple = (listing_title, listing_id)
                    if listing_tuple not in results:
                        results.append(listing_tuple)
    return results


def get_listing_details(listing_id) -> dict:
   
    base_dir = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(base_dir, "html_files", f"listing_{listing_id}.html")
    with open(path, "r", encoding="utf-8-sig") as file:

        soup = BeautifulSoup(file.read(), "html.parser")
    text = soup.get_text()
    if "Superhost" in text:
        host_type = "Superhost"
    else:
        host_type = "regular"


    host_name = ""
    if "Hosted by"  in text:
        host_name = text.split("Hosted by")[1].split("\n")[0].strip()

    if "Private" in text:
        room_type = "Private Room"
    elif "Shared" in text:
        room_type = "Shared Room"
    else:
        room_type = "Entire Room"

    location_rating = 0.0
    lines = soup.get_text("\n").split("\n")
    for i in range(len(lines)):
        if lines[i].strip() == "Location":
            for j in range(i + 1, min(i + 12, len(lines))):
                line = lines[j].strip()
                try:
                    num = float(line)
                    if 0.0 <= num <= 5.0:
                        location_rating = num
                        break
                except: 
                    continue
            if location_rating != 0.0:
                break

   
    
    
    

    policy_number = "Pending"
    if "Pending" in text:
        policy_number = "Pending"
    elif "Exempt" in text:
        policy_number = "Exempt"
    else:
        for word in text.split():
            if "STR" in word:
                policy_number = word[:11]
                break

    return {
        listing_id: {
            "policy_number": policy_number,
            "host_type": host_type,
            "host_name": host_name,
            "room_type": room_type,
            "location_rating": location_rating
        }
    }





def create_listing_database(html_path) -> list[tuple]:
    database = []
    listings = load_listing_results(html_path)
    for title, listing_id in listings:
        details = get_listing_details(listing_id)[listing_id]
        database.append((
            title,
            listing_id,
            details["policy_number"],
            details["host_type"],
            details["host_name"],
            details["room_type"],
            details["location_rating"]
        ))

   

    return database


def output_csv(data, filename) -> None:
    sorted_data = sorted(data, key=lambda x: x[-1], reverse=True)
    with open(filename, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Listing Title",
            "Listing ID",
            "Policy Number",
            "Host Type",
            "Host Name",
            "Room Type",
            "Location Rating"

        ])

        for row in sorted_data:
            writer.writerow(row)

    



def avg_location_rating_by_room_type(data) -> dict:
    totals = {}
    counts = {}
    for row in data:
        room_type = row[5]
        rating = row[6]
        if rating == 0.0:
            continue
        if room_type not in totals:
            totals[room_type] = 0
            counts[room_type] = 0

        totals[room_type] += rating
        counts[room_type] += 1
    
    averages = {}
    for room_type in totals:
        averages[room_type] = totals[room_type] / counts[room_type]

    return averages



def validate_policy_numbers(data) -> list[str]:
   invalid = []
   for row in data:
       listing_id = row[1]
       policy = row[2]
       if policy == "Pending" or policy == "Exempt":
           continue
       
       valid = False
       if len(policy) == 13 and policy.startswith("20") and policy.endswith("STR"):
           valid = True

       if policy.startswith("STR-00") and len(policy) == 13:
           valid = True

       if not valid:
           invalid.append(listing_id)
 
   return invalid

        


        
           
            
           

# EXTRA CREDIT
def google_scholar_searcher(query):
    url = "https://scholar.google.com/scholar?q=" + query
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    titles = []
    results = soup.find_all("h3")
    for result in results:
        title = result.get_text()
        if title:
            titles.append(title)

    return titles
 

class TestCases(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.abspath(os.path.dirname(__file__))
        self.search_results_path = os.path.join(self.base_dir, "html_files", "search_results.html")

        self.listings = load_listing_results(self.search_results_path)
        self.detailed_data = create_listing_database(self.search_results_path)

    def test_load_listing_results(self):
        # TODO: Check that the number of listings extracted is 18.
        # TODO: Check that the FIRST (title, id) tuple is  ("Loft in Mission District", "1944564").
        self.assertEqual(len(self.listings), 18)
        self.assertEqual(self.listings[0], ("Loft in Mission District", "1944564"))

    def test_get_listing_details(self):
        html_list = ["467507", "1550913", "1944564", "4614763", "6092596"]

        results = []
        for listing_id in html_list:
            results.append(get_listing_details(listing_id))

        self.assertEqual(results[0]["467507"]["policy_number"], "STR-0005349")
        self.assertEqual(results[2]["1944564"]["host_type"], "Superhost")
        self.assertEqual(results[2]["1944564"]["room_type"], "Entire Room")
        self.assertEqual(results[2]["1944564"]["location_rating"], 4.9)

    def test_create_listing_database(self):
        # TODO: Check that each tuple in detailed_data has exactly 7 elements:
        # (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)

        # TODO: Spot-check the LAST tuple is ("Guest suite in Mission District", "467507", "STR-0005349", "Superhost", "Jennifer", "Entire Room", 4.8).
        pass

    def test_output_csv(self):
        out_path = os.path.join(self.base_dir, "test.csv")

        # TODO: Call output_csv() to write the detailed_data to a CSV file.
        # TODO: Read the CSV back in and store rows in a list.
        # TODO: Check that the first data row matches ["Guesthouse in San Francisco", "49591060", "STR-0000253", "Superhost", "Ingrid", "Entire Room", "5.0"].

        if os.path.exists(out_path):
            os.remove(out_path)

    def test_avg_location_rating_by_room_type(self):
        # TODO: Call avg_location_rating_by_room_type() and save the output.
        # TODO: Check that the average for "Private Room" is 4.9.
        pass

    def test_validate_policy_numbers(self):
        # TODO: Call validate_policy_numbers() on detailed_data and save the result into a variable invalid_listings.
        # TODO: Check that the list contains exactly "16204265" for this dataset.
        pass


def main():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(base_dir, "html_files", "search_results.html")
    detailed_data = create_listing_database(path)
    output_csv(detailed_data, "airbnb_dataset.csv")


if __name__ == "__main__":
    main()
    unittest.main(verbosity=2)