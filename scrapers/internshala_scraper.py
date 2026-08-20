"""
Scraper to fetch internships from Internshala
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import re
from dotenv import load_dotenv
import cohere
from datetime import datetime
import time

load_dotenv()

# Global configuration - change this to scrape more/fewer internships
MAX_INTERNSHIPS = 300

def parse_stipend(stipend_text: str) -> dict:
    """
    Parse a stipend string like '₹ 12,000 /month' or 'Unpaid' into
    a structured dict compatible with the pipeline normalizer.
    """
    if not stipend_text:
        return {"type": "unpaid", "amount": None, "currency": "INR", "period": None}

    text = stipend_text.strip()

    if re.search(r'unpaid|volunteer|no stipend', text, re.IGNORECASE):
        return {"type": "unpaid", "amount": None, "currency": "INR", "period": None}

    if re.search(r'performance|incentive', text, re.IGNORECASE):
        return {"type": "performance-based", "amount": None, "currency": "INR", "period": None}

    # Detect currency
    currency = "INR"
    if "$" in text or "USD" in text:
        currency = "USD"
    elif "£" in text or "GBP" in text:
        currency = "GBP"
    elif "€" in text or "EUR" in text:
        currency = "EUR"

    # Extract numeric amount — handles ranges like "10,001 - 11,002" (take lower bound)
    clean = text.replace(',', '')
    amount_match = re.search(r'(\d+)', clean)
    amount = int(amount_match.group(1)) if amount_match else None

    # Detect period
    period = None
    if re.search(r'/month|per month|monthly', text, re.IGNORECASE):
        period = "monthly"
    elif re.search(r'/week|per week|weekly', text, re.IGNORECASE):
        period = "weekly"
    elif re.search(r'/day|per day|daily', text, re.IGNORECASE):
        period = "daily"
    elif re.search(r'lump.?sum|one.?time|total', text, re.IGNORECASE):
        period = "lump-sum"

    return {
        "type": "paid" if amount else "unpaid",
        "amount": amount,
        "currency": currency,
        "period": period,
    }


from concurrent.futures import ThreadPoolExecutor, as_completed

def _fetch_detail_page(item: dict, session: requests.Session, headers: dict) -> dict:
    """Fetch detail page concurrently for a single internship item."""
    apply_link = item.get("apply_link")
    if not apply_link or apply_link == "https://internshala.com":
        return item

    try:
        detail_resp = session.get(apply_link, headers=headers, timeout=6)
        if detail_resp.status_code != 200:
            return item

        detail_soup = BeautifulSoup(detail_resp.content, 'html.parser')
        main_container = detail_soup.find('div', class_='detail_view') or detail_soup.find('div', class_='internship_details') or detail_soup

        # Location
        detail_location = main_container.find('div', id='location_names')
        if detail_location:
            loc_link = detail_location.find('a')
            if loc_link:
                item["location"] = loc_link.text.strip()

        # Duration & Deadline & Stipend
        detail_items = main_container.find_all('div', class_='other_detail_item')
        duration_found = False
        for d_item in detail_items:
            heading = d_item.find('span')
            if not heading:
                continue
            heading_text = heading.text.lower()

            if 'duration' in heading_text and not duration_found:
                body = d_item.find('div', class_='item_body')
                if body:
                    item["duration_string"] = body.text.strip()
                    duration_found = True
            elif 'apply by' in heading_text:
                body = d_item.find('div', class_='item_body')
                if body:
                    item["deadline_text"] = body.text.strip()
            elif 'stipend' in heading_text:
                stip_span = d_item.find('span', class_='stipend')
                if stip_span:
                    item["stipend_text"] = stip_span.text.strip()
                    item["stipend"] = parse_stipend(item["stipend_text"])

        # Skills
        skills_heading = main_container.find('h3', class_='skills_heading')
        if skills_heading:
            skills_container = skills_heading.find_next_sibling('div', class_='round_tabs_container')
            if skills_container:
                extracted = [s.text.strip() for s in skills_container.find_all('span', class_='round_tabs') if s.text.strip()]
                if extracted:
                    item["skills"] = extracted

        # Perks
        perks_heading = main_container.find('h3', class_='perks_heading')
        if perks_heading:
            perks_container = perks_heading.find_next_sibling('div', class_='round_tabs_container')
            if perks_container:
                item["perks"] = [p.text.strip() for p in perks_container.find_all('span', class_='round_tabs') if p.text.strip()]

        # Openings
        openings_heading = main_container.find('h3', string=lambda t: t and 'number of openings' in t.lower())
        if openings_heading:
            openings_div = openings_heading.find_next_sibling('div', class_='text-container')
            if openings_div:
                try:
                    item["openings"] = int(openings_div.text.strip())
                except ValueError:
                    pass

        # Responsibilities
        about_heading = main_container.find('h2', class_='about_heading')
        if about_heading:
            desc_div = about_heading.find_next_sibling('div', class_='text-container')
            if desc_div:
                text = desc_div.get_text(separator='\n', strip=True)
                item["responsibilities"] = [line.strip() for line in text.split('\n') if line.strip()]

        # Company info
        company_heading = main_container.find('h2', string=lambda t: t and 'about' in t.lower() and item["company"].lower() in t.lower())
        if company_heading:
            website_div = company_heading.find_next_sibling('div', class_='website_link')
            if website_div:
                link = website_div.find('a')
                if link:
                    item["company_website"] = link.get('href', '').strip()

            about_div = company_heading.find_next_sibling('div', class_='about_company_text_container')
            if about_div:
                item["about_company"] = about_div.text.strip()

    except Exception as exc:
        pass
    return item


def scrape_internshala_internships(max_internships=None):
    """Scrape internships from Internshala with session pooling & concurrency."""

    if max_internships is None:
        max_internships = MAX_INTERNSHIPS

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(pool_connections=20, pool_maxsize=20)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    url = "https://internshala.com/internships/software-development-internship/"
    print(f"Fetching internships from Internshala...")

    try:
        response = session.get(url, headers=headers, timeout=8)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        internship_cards = soup.find_all('div', class_='individual_internship')
        print(f"Found {len(internship_cards)} internship cards")

        base_items = []
        for card in internship_cards[:max_internships]:
            try:
                internship_id = card.get('internshipid', '')
                title_elem = card.find('a', class_='job-title-href')
                if title_elem:
                    position = title_elem.text.strip()
                    href = title_elem.get('href', '') or card.get('data-href', '')
                else:
                    position = "Software Internship"
                    href = card.get('data-href', '')

                apply_link = ("https://internshala.com" + href) if href else "https://internshala.com"
                company_elem = card.find('p', class_='company-name')
                company = company_elem.text.strip() if company_elem else "Unknown Company"

                row_items = card.find_all('div', class_='row-1-item')
                location_text = "Remote"
                for item in row_items:
                    if 'locations' in item.get('class', []):
                        location_text = item.get_text(separator=' ', strip=True)
                        break

                is_remote = bool(re.search(r'work from home|remote|wfh', location_text, re.IGNORECASE))
                stipend_elem = card.find('span', class_='stipend')
                stipend_text = stipend_elem.text.strip() if stipend_elem else ""
                stipend = parse_stipend(stipend_text)

                duration_text = ""
                non_location_items = [i for i in row_items if 'locations' not in i.get('class', [])]
                for item in non_location_items:
                    span = item.find('span')
                    if span and not span.get('class'):
                        duration_text = span.text.strip()
                        break

                card_skills = [s.text.strip() for s in card.find_all('div', class_='job_skill') if s.text.strip()]

                base_items.append({
                    "internship_id": internship_id,
                    "company": company,
                    "name": position,
                    "location": location_text,
                    "is_remote": is_remote,
                    "apply_link": apply_link,
                    "stipend_text": stipend_text,
                    "stipend": stipend,
                    "duration_string": duration_text,
                    "skills": card_skills,
                    "deadline_text": "",
                    "perks": [],
                    "openings": None,
                    "responsibilities": [],
                    "about_company": "",
                    "company_website": "",
                    "source": "web_scraping",
                })
            except Exception as e:
                print(f"Error parsing card: {e}")
                continue

        # Concurrent detail page fetching
        print(f"Fetching details for {len(base_items)} items concurrently...")
        internships = []
        with ThreadPoolExecutor(max_workers=12) as executor:
            futures = [executor.submit(_fetch_detail_page, item, session, headers) for item in base_items]
            for future in as_completed(futures):
                try:
                    internships.append(future.result())
                except Exception as exc:
                    pass

        print(f"Successfully scraped {len(internships)} internships from Internshala")
        return internships

    except Exception as e:
        print(f"Error scraping Internshala: {e}")
        return []



def fast_heuristic_enrichment(internship: dict) -> dict:
    """Instant local enrichment without external API latency."""
    name = (internship.get("name") or "").lower()
    company = internship.get("company", "Company")
    location = (internship.get("location") or "remote").lower()

    degree = ["Bachelor's degree in Computer Science or related field"]
    field = ["Computer Science", "Software Engineering"]

    if "market" in name or "sales" in name:
        field = ["Marketing", "Business Development"]
        degree = ["Bachelor's degree in Business, Marketing, or related field"]
    elif "design" in name or "ui" in name or "ux" in name:
        field = ["Design", "User Experience"]
        degree = ["Bachelor's degree in Design, Fine Arts, or related field"]
    elif "data" in name or "analyst" in name:
        field = ["Data Science", "Analytics"]
        degree = ["Bachelor's degree in Data Science, Statistics, or CS"]

    responsibilities = internship.get("responsibilities")
    if isinstance(responsibilities, list) and responsibilities:
        summary = " ".join(responsibilities[:3])[:200]
    else:
        summary = f"Software engineering internship at {company} involving hands-on development."

    city = "remote" if any(w in location for w in ["work from home", "remote", "wfh"]) else location.strip()

    return {
        "degree": degree,
        "field": field,
        "summary": summary,
        "country": "india",
        "city": city,
    }


def enrich_with_ai(internships, co=None):
    """Use Cohere to enrich internship data with fast local fallback."""
    if not co or not os.getenv("COHERE_API_KEY"):
        return [fast_heuristic_enrichment(item) for item in internships]

    prompt = f"""Given these internship postings:
{json.dumps(internships, indent=2)}

Generate a JSON array of objects (one per internship, in the same order) with these fields:
- degree: array of degree requirements (e.g. ["Bachelor's in Computer Science or related field"])
- field: array of 1-3 relevant fields of study (e.g. ["Computer Science", "Software Engineering"])
- summary: 50-70 word summary of what this internship involves (use the responsibilities field if available)
- country: country name in lowercase (default "india" if location is an Indian city)
- city: city name(s) in lowercase, comma-separated if multiple (e.g. "mumbai, delhi", "navi mumbai", "remote" for work from home)

Return ONLY the JSON array, no other text."""

    try:
        response = co.chat(
            model='command-a-03-2025',
            message=prompt,
            max_tokens=1500,
            temperature=0.3,
        )

        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()

        enriched_data = json.loads(response_text)
        if isinstance(enriched_data, dict):
            enriched_data = [enriched_data]
        return enriched_data

    except Exception as e:
        print(f"Error enriching internships with Cohere: {e} — using fast heuristic fallback")
        return [fast_heuristic_enrichment(item) for item in internships]



def main():
    cohere_api_key = os.getenv("COHERE_API_KEY")
    co = cohere.Client(cohere_api_key)

    raw_internships = scrape_internshala_internships()

    print("Raw internships:")
    print(json.dumps(raw_internships, indent=2))

    if not raw_internships:
        print("No internships found from Internshala.")
        return []

    print("\nEnriching internships with AI...")
    enriched_data = enrich_with_ai(raw_internships, co)

    enriched_internships = []

    for i, internship in enumerate(raw_internships):
        enriched = enriched_data[i] if i < len(enriched_data) else {}

        # Parse deadline_text to Date if present (e.g. "28 May' 26" -> 2026-05-28)
        deadline_date = None
        if internship.get("deadline_text"):
            try:
                # Parse formats like "28 May' 26" or "3 Jun' 26"
                deadline_str = internship["deadline_text"]
                # Replace ' with space and parse
                deadline_str = deadline_str.replace("'", " ")
                deadline_date = datetime.strptime(deadline_str, "%d %b %y").isoformat()
            except:
                pass

        # Ensure summary is a string
        summary = enriched.get("summary", "")
        if not isinstance(summary, str):
            # If AI returned something weird, generate from responsibilities
            if isinstance(internship.get("responsibilities"), list):
                summary = " ".join(internship["responsibilities"][:3])[:150]
            else:
                summary = f"Software engineering internship at {internship['company']}."

        # Extract city from location, handling multi-word cities and multiple cities
        city = enriched.get("city", "")
        if not city or not isinstance(city, str):
            # Fallback: use location field
            location = internship.get("location", "remote").lower()
            # Handle "work from home" -> "remote"
            if "work from home" in location or "wfh" in location or "remote" in location:
                city = "remote"
            elif "," in location:
                # Multiple cities: keep all, clean up spacing (e.g. "Mumbai, Delhi" -> "mumbai, delhi")
                cities = [c.strip() for c in location.split(",")]
                city = ", ".join(cities)
            else:
                # Keep full city name (e.g. "navi mumbai" not just "navi")
                city = location.strip()

        final_internship = {
            "name": internship["name"],
            "company": internship["company"],
            "apply_link": internship.get("apply_link", ""),
            "date_published": datetime.now().isoformat(),
            "deadline_date": deadline_date,
            "country": enriched.get("country", "india"),
            "city": city,
            "state": None,  # Not available in Internshala HTML
            "is_remote": internship.get("is_remote", False),
            "skills": internship.get("skills", []),
            "degree": enriched.get("degree", []),
            "field": enriched.get("field", []),
            "summary": summary,
            "responsibilities": internship.get("responsibilities"),  # Now an array
            "perks": internship.get("perks"),
            "openings": internship.get("openings"),
            "stipend": internship.get("stipend", {"type": "unpaid", "amount": None, "currency": "INR", "period": None}),
            "duration_string": internship.get("duration_string", ""),  # Pipeline normalizer will parse this
            "source": "web_scraping",
        }

        enriched_internships.append(final_internship)

    print(f"\nSuccessfully enriched {len(enriched_internships)} internships")

    output_file = "data/internships_internshala.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(enriched_internships, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Scraped and enriched {len(enriched_internships)} internships from Internshala")
    print(f"✓ Saved to {output_file}")

    return enriched_internships

if __name__ == "__main__":
    main()
