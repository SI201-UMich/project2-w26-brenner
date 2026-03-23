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
                listing_id = href.split("/rooms/")[1].split("?")[0]
                listing_title = link.get_text(strip=True)
                if listing_title:
                    listing_tuple = (listing_title, listing_id)
                    if listing_tuple not in results:
                        results.append(listing_tuple)
    return results


def get_listing_details(listing_id) -> dict:
   
    with open(f"html_files/listing_{listing_id}.html", "r", encoding="utf-8-sig") as file:
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
    if "Location" in text:
        try:
            location_rating = float(text.split("Location")[1].strip()[0:3])
        except: 
            location_rating = 0.0

    policy_number = "Pending"
    if "Pending" in text:
        policy_number = "Pending"
    elif "Exempt" in text:
        policy_number = "Exempt"
    else:
        for word in text.split():
            if "STR" in word:
                policy_number = word

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
    listing_titles = get_listing_titles(html_path)
    listing_ids = get_listing_ids(html_path)
    policy_numbers = get_policy_numbers(html_path)
    host_types = get_host_types(html_path)
    host_names = get_host_names(html_path)
    room_types = get_room_types(html_path)
    location_ratings = get_location_ratings(html_path)

    for i in range(len(listing_titles)):
        database.append((
            listing_titles[i],
            listing_ids[i],
            policy_numbers[i],
            host_types[i],
            host_names[i],
            room_types[i],
            location_ratings[i],
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
    """
    EXTRA CREDIT

    Args:
        query (str): The search query to be used on Google Scholar
    Returns:
        List of titles on the first page (list)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


class TestCases(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.abspath(os.path.dirname(__file__))
        self.search_results_path = os.path.join(self.base_dir, "html_files", "search_results.html")

        self.listings = load_listing_results(self.search_results_path)
        self.detailed_data = create_listing_database(self.search_results_path)

    def test_load_listing_results(self):
        # TODO: Check that the number of listings extracted is 18.
        # TODO: Check that the FIRST (title, id) tuple is  ("Loft in Mission District", "1944564").
        pass

    def test_get_listing_details(self):
        html_list = ["467507", "1550913", "1944564", "4614763", "6092596"]

        # TODO: Call get_listing_details() on each listing id above and save results in a list.

        # TODO: Spot-check a few known values by opening the corresponding listing_<id>.html files.
        # 1) Check that listing 467507 has the correct policy number "STR-0005349".
        # 2) Check that listing 1944564 has the correct host type "Superhost" and room type "Entire Room".
        # 3) Check that listing 1944564 has the correct location rating 4.9.
        pass

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
    detailed_data = create_listing_database(os.path.join("html_files", "search_results.html"))
    output_csv(detailed_data, "airbnb_dataset.csv")


if __name__ == "__main__":
    main()
    unittest.main(verbosity=2)