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
               text_block = link.find_next("div").get_text("\n", strip=True)
               listing_title = text_block.split("\n")[0].strip()

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
    lines = soup.get_text("\n").split("\n")
    for i in range(len(lines)):
        if "Hosted by" in lines [i]:
            after = lines[i].split("Hosted by")[-1].strip()
            if after:
                host_name = after.split("Joined")[0].strip()
            else:
                for j in range(i+1, len(lines)):
                    if lines[j].strip():
                        host_name = lines[j].strip().split("Joined")[0].strip()
                        break
            break
    room_type = "Entire Room"
    non_empty_lines=[]
    for line in lines:
        clean_line = line.strip()
        if clean_line:
            non_empty_lines.append(clean_line)

    subtitle = ""
    for line in non_empty_lines[:30]:
        if " in " in line:
            subtitle = line
            break
    if "Private" in subtitle: 
        room_type = "Private Room"
    elif "Shared" in subtitle:
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

   
    
    
    

    policy_number = ""
    match = re.search(r"20\d{2}-00\d{4}STR|STR-\d{7}", text)
    if match:
        policy_number = match.group()
    else:
        lines = soup.get_text("\n").split("\n")
        for i in range(len(lines)):
            clean_line = lines[i].strip()
            if "policy" in clean_line.lower() or "license" in clean_line.lower():
                for j in range(i, min(i+5, len(lines))):
                    nearby = lines[j].strip()
                    if re.search(r"\b[Pp]ending\b", nearby):
                        policy_number = "Pending"
                        break
                    elif re.search(r"\b[Ee]xempt\b", nearby):
                        policy_number = "Exempt"
                        break
                if policy_number:
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
        averages[room_type] =round(totals[room_type] / counts[room_type], 1)

    return averages



def validate_policy_numbers(data) -> list[str]:
   invalid = []
   for row in data:
       listing_id = row[1]
       policy = row[2]
       if policy == "Pending" or policy == "Exempt":
           continue
       
       valid = False
       if re.fullmatch(r"20\d{2}-00\d{4}STR", policy):
           valid = True
       elif re.fullmatch(r"STR-\d{7}", policy):
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
        for row in self.detailed_data:
            self.assertEqual(len(row), 7)

        self.assertEqual(self.detailed_data[-1], ("Guest suite in Mission District", "467507", "STR-0005349", "Superhost", "Jennifer", "Entire Room", 4.8))

    def test_output_csv(self):
        out_path = os.path.join(self.base_dir, "test.csv")
        output_csv(self.detailed_data, out_path)
        rows=[]
        with open(out_path, "r", encoding="utf-8-sig") as file:
            reader = csv.reader(file)
            for row in reader:
                rows.append(row)

            self.assertEqual(rows[1], ["Guesthouse in San Francisco", "49591060", "STR-0000253", "Superhost", "Ingrid", "Entire Room", "5.0"] )


        if os.path.exists(out_path):
            os.remove(out_path)

    def test_avg_location_rating_by_room_type(self):
        result = avg_location_rating_by_room_type(self.detailed_data)
        self.assertEqual(result["Private Room"], 4.9)

    def test_validate_policy_numbers(self):
        invalid_listings = validate_policy_numbers(self.detailed_data)
        self.assertEqual(invalid_listings, ["16204265"])


def main():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(base_dir, "html_files", "search_results.html")
    detailed_data = create_listing_database(path) 
    output_csv(detailed_data, "airbnb_dataset.csv")


if __name__ == "__main__":
    main()
    unittest.main(verbosity=2)