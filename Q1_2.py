from bs4 import BeautifulSoup
import urllib.request

# here is the meta url for press room
meta_url = "https://www.europarl.europa.eu/news/en/press-room/page/<page_number>"

urls = []  # queue of press release urls to crawl
seen = []  # stack of press release urls seen so far
opened = []  # we keep track of seen press release urls so that we don't revisit them
saved = []  # saved urls that are plenary sessions and contain the word "crisis"

# here is the anchor for press release and target word for content check
anchor = '<span class="ep_name">Plenary session</span>'
target_word = "crisis"

# set the maximum number of urls to save
maxNumUrl = 10
# set the counter for saved file
savedUrlCounter = 1
# set the counter for press room page
pageCounter = 0


while len(saved) < maxNumUrl:
    # collect press release urls
    press_room_url = meta_url.replace("<page_number>", str(pageCounter))
    pageCounter += 1
    try:
        print("Trying to access= " + press_room_url)
        req = urllib.request.Request(
            press_room_url, headers={"User-Agent": "Mozilla/5.0"}
        )
        press_room_webpage = urllib.request.urlopen(req).read()

    except Exception as ex:
        print("Unable to access= " + press_room_url)
        print(ex)
        continue  # skip code below

    # creates object press_room_soup
    press_room_soup = BeautifulSoup(press_room_webpage, "html.parser")
    # put press release URLs into the stack
    for tag in press_room_soup.find_all("a", href=True):  # find tags with links
        press_release_url = tag["href"]  # extract just the link
        if press_release_url not in seen:
            urls.append(press_release_url)
            seen.append(press_release_url)

    # go through each press release in the current page of press room
    while urls and len(saved) < maxNumUrl:
        try:
            curr_url = urls.pop(0)
            print("Trying to access= " + curr_url)
            req = urllib.request.Request(
                curr_url, headers={"User-Agent": "Mozilla/5.0"}
            )
            press_release_webpage = urllib.request.urlopen(req).read()
            opened.append(curr_url)

        except Exception as ex:
            print("Unable to access= " + curr_url)
            print(ex)
            continue  # skip code below

        # creates object press_release_soup
        press_release_soup = BeautifulSoup(press_release_webpage, "html.parser")
        # check if the page is plenary session
        if anchor in str(press_release_soup):
            # collect all the necessary parts of the press release
            # some paragraphs have two parts: text_0 and text_1 below
            try:
                press_release_title = press_release_soup.find(
                    "h1", class_="ep_title"
                ).text.lower()
            except:
                press_release_title = ""
            try:
                press_release_fact = press_release_soup.find(
                    class_="ep-a_facts"
                ).text.lower()
            except:
                press_release_fact = ""
            try:
                press_release_text_0 = press_release_soup.find_all(class_="ep-a_text")[
                    0
                ].text.lower()
            except:
                press_release_text_0 = ""
            try:
                press_release_text_1 = press_release_soup.find_all(class_="ep-a_text")[
                    1
                ].text.lower()
            except:
                press_release_text_1 = ""

            # check if the title, fact, and paragraphs contain the word "crisis"
            if (
                target_word in press_release_title
                or target_word in press_release_fact
                or target_word in press_release_text_0
                or target_word in press_release_text_1
            ):
                saved.append(curr_url)
                # output html source code to text file
                with open(
                    "2_" + str(savedUrlCounter) + ".txt",
                    "w",
                    encoding="utf-8",
                    errors="ignore",
                ) as file:
                    file.write(str(press_release_soup))
                    savedUrlCounter += 1

# print summary
print("\nSummary:")
print(
    "num. of URLs seen = %d, scanned = %d, and saved = %d"
    % (len(seen), len(opened), len(saved))
)
print("saved urls:")
for url in saved:
    print(url)
