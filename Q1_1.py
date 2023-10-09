from bs4 import BeautifulSoup
import urllib.request


seed_url = "https://press.un.org/en"

urls = [seed_url]  # queue of urls to crawl
seen = [seed_url]  # stack of urls seen so far
opened = []  # we keep track of seen urls so that we don't revisit them
saved = []  # saved urls that are press release and contain the word "crisis"

# here is the anchor for page and target word for content check
anchor = '<a href="/en/press-release" hreflang="en">Press Release</a>'
target_word = "crisis"

# set the maximum number of urls to save
maxNumUrl = 10
# set the counter for saved urls
savedUrlCounter = 1

print("Starting with the seed url= " + seed_url)
while len(urls) > 0 and len(saved) < maxNumUrl:
    try:
        curr_url = urls.pop(0)
        print("Trying to access= " + curr_url)
        req = urllib.request.Request(curr_url, headers={"User-Agent": "Mozilla/5.0"})
        webpage = urllib.request.urlopen(req).read()
        opened.append(curr_url)

    except Exception as ex:
        print("Unable to access= " + curr_url)
        print(ex)
        continue  # skip code below

    # IF URL OPENS, CHECK WHICH URLS THE PAGE CONTAINS
    # ADD THE URLS FOUND TO THE QUEUE url AND seen
    soup = BeautifulSoup(webpage, "html.parser")  # creates object press_room_soup
    # Put child URLs into the stack
    for tag in soup.find_all("a", href=True):  # find tags with links
        childUrl = tag["href"]  # extract just the link
        o_childurl = childUrl
        childUrl = urllib.parse.urljoin(seed_url, childUrl)
        if seed_url in childUrl and childUrl not in seen:
            urls.append(childUrl)
            seen.append(childUrl)

    # check if the page is press release
    if anchor in str(soup):
        # check if the headline and paragraphs contain the word "crisis"
        press_release_headline = soup.find("h1", class_="page-header").text.lower()
        press_release_paragraphs = soup.find(
            class_="field field--name-body field--type-text-with-summary field--label-hidden field__item"
        ).text.lower()
        if (
            target_word in press_release_headline
            or target_word in press_release_paragraphs
        ):
            saved.append(curr_url)
            # output html source code to text file
            with open(
                "1_" + str(savedUrlCounter) + ".txt",
                "w",
                encoding="utf-8",
                errors="ignore",
            ) as file:
                file.write(str(soup))
                savedUrlCounter += 1

print("\nSummary:")
print(
    "num. of URLs seen = %d, scanned = %d, and saved = %d"
    % (len(seen), len(opened), len(saved))
)
print("saved urls:")
for url in saved:
    print(url)
