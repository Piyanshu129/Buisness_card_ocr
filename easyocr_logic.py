import easyocr
import numpy as np
import re



def get_easyocr_reader():
    """Initializes and caches the EasyOCR reader."""
    return easyocr.Reader(['en'], gpu=True)
def extract_text_easyocr(image):
    reader = get_easyocr_reader()
    results = reader.readtext(np.array(image), detail=1)
    extracted = []
    logo_keywords = ['quality', 'excellence', 'innovation', 'growth', 'service', 'assurance', 'pvt', 'inc', 'llc','Ajwain','LED',
                     'ltd','packaging','solar','wooden','types','Kamalwade','cards','chillies','Fittings','Stainless','Fancy','steel','%','fax','deals','Kalonji']
    for _, text, conf in results:
        if not any(re.search(rf"\b{keyword}\b", text.strip().lower()) for keyword in logo_keywords): extracted.append(
            text.strip())
    return extracted


def categorize_with_easyocr(lines):
    def clean_email(email):
        if '@' not in email: return email
        local, domain = email.split('@', 1)
        if '.' not in domain:
            for tld in ['com', 'in', 'org', 'net', 'co']:
                if domain.endswith(tld):
                    domain = domain[:-len(tld)] + '.' + tld
                    break
        return local + '@' + domain

    def normalize_website(raw):
        return re.sub(r"\s+", "", raw.lower().strip())

    def extract_emails_and_websites(text_lines):
        emails, websites = [], []

        email_pattern = re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z0-9-.]+\b")
        website_pattern = re.compile(r"https?://[a-zA-Z0-9\-\.\_/]+|\b[a-zA-Z0-9.-]+\.[a-z]{2,}\b")

        # List of unwanted domains in the website field
        unwanted_websites = ["101.ph","b.com","g.vrtraders","s.kbrokers","m.narayana","m.se"]


        for line in text_lines:
            line_lower = line.lower()
            cleaned_line = re.sub(r'(?i)(email|supportemail|emailid|web|website)\s*[:\-]?', '', line_lower)

            found_emails = email_pattern.findall(cleaned_line)
            emails.extend(found_emails)

            if '@' in cleaned_line and not found_emails:
                cleaned_line = cleaned_line.replace(' ', '')
                if '@' in cleaned_line:
                    emails.append(cleaned_line)

            found_sites = website_pattern.findall(line_lower)
            # Exclude unwanted website entries
            filtered_websites = [site for site in found_sites if site not in unwanted_websites and '@' not in site]

            websites.extend([normalize_website(site) for site in filtered_websites])

        emails = list(set([clean_email(e) for e in emails]))
        websites = list(set(websites))

        return emails, websites

    data = {"Name": "", "Email": [], "Phone": [], "Address": [], "Website": [], "Pincode": []}
    address_keywords = ['office', 'Corporate Office', 'bldg', 'road', 'rd', 'st', 'sector', 'house', 'plot', 'near','nagar',
                        'park', 'nagar', 'building', 'complex', 'village', 'area', 'hall', 'block', 'lane', 'layout',
                        'mumbai', 'vashi', 'opp', 'city', 'galli', 'Flat', 'Apartments', 'street', '#', 'gaon','flat','road',
                        'market', 'phase','gunj','shop','plaza','bazar','Periyasamy']

    def extract_full_address(lines_to_search):
        address_block, address_started = [], False
        for line in lines_to_search:
            if not address_started and re.search(r'\bAdd\b[:：]?', line, re.IGNORECASE):
                address_started = True
                address_block.append(re.sub(r'\bAdd\b[:：]?', '', line, flags=re.IGNORECASE).strip())
            elif address_started:
                if re.search(r'\b(Contact|Phone|Email|Support|Web|www|@|[0-9]{10}|Pincode)\b', line,
                             re.IGNORECASE): break
                address_block.append(line.strip())
        return address_block

    emails, websites = extract_emails_and_websites(lines)
    data["Email"].extend(emails)
    data["Website"].extend(
        [s for s in websites if not any(s.endswith(d) for d in ['yahoo.com', 'gmail.com', 'rediffmail.com'])])

    all_phones, all_pincodes = [], []
    for line in lines:
        all_phones.extend(
            re.findall(r"(?:\+91[\s\-]?)?(?:\d{5}[\s\-]?\d{5}|\b\d{10}\b|\b\d{7}\b|\b\d{4}[\-\s]?\d{7}\b|\b\d{11}\b|\b\d{3}[\-\s]?\d{3}[\-\s]?\d{4}\b|\+91[\s]?\d{2}[\s]?\d{8}|\(?\d{3,5}\)?[\s\-]?\d{5,7})", line))
        all_pincodes.extend(re.findall(r"\b\d{6}\b|\b\d{3}[\s\-]?\d{3}\b", line))
        # if not data["Name"] and len(line.split()) > 1 and len(line) > 3 and line[0].isupper() and not any(
        #     c.isdigit() for c in line) and '@' not in line: data["Name"] = line
        for line in lines:
            line_cleaned = re.sub(r'[^a-zA-Z\s]', '', line).strip()  # Remove unwanted symbols & numbers
            if len(line_cleaned.split()) > 1 and len(line) > 3 and line_cleaned[0].isupper() and not any(
                    kw in line_cleaned.lower() for kw in address_keywords):
                data["Name"] = line_cleaned.title()  # Proper capitalization
                break

                # if not data["Name"]:
    #     for email in data["Email"]:
    #         if "gmail.com" in email:
    #             username = email.split("@")[0]
    #             # Convert from "john.doe" to "John Doe"
    #             formatted_name = " ".join([part.capitalize() for part in re.split(r'[._\s\-]', username)])
    #             data["Name"] = formatted_name
    #             break
    address_block = extract_full_address(lines)
    if address_block:
        data["Address"] = address_block
    else:
        for line in lines:
            is_other_info = (data["Name"] == line or any(e in line for e in data["Email"]) or any(
                p in line for p in all_phones) )
            if not is_other_info and any(kw in line.lower() for kw in address_keywords): data["Address"].append(line)

    return {"Name": data["Name"], "Email": ', '.join(set(data["Email"])), "Phone": ', '.join(set(all_phones)),
            "Address": ', '.join(set(data["Address"])), "Website": ', '.join(set(data["Website"])),
            "Pincode": ', '.join(set(all_pincodes))}

