import requests
from bs4 import BeautifulSoup as bs
import re
import pandas as pd
import os.path
from datetime import datetime

# Skapa listor
gameTitle = []
rating = []
discountPercent = []
discountPrice = []
originalPrice = []
releaseDate = []
reviewsListRaw = []
reviewsList = []
windowsSupport = []
macSupport = []
linuxSupport = []
windowsList = []
macList = []
linuxList = []
scrapeDate = []

# Loop igenom sidorna 1-5
for page in range(1, 6):
    # URLen är nästan samma för alla sidorna, ända som ändras är sidnumret i slutet vilket för det lätt att byta sida med en enkel for-loop
    data = requests.get('https://store.steampowered.com/search/?specials=1&page=' + str(page))
    soup = bs(data.content, 'html.parser')
    # Söker fram den rätta div'en där infon vi söker finns
    divs = soup.find_all('div', class_='responsive_search_name_combined')
    # Sedan loopar vi genom de hittade div'en
    for i in divs:
        # Om 'col search_price discounted responsive_secondrow' har innehåll vet vi att det är ett spel
        if i.find('div', class_='col search_price discounted responsive_secondrow') is not None:
            # Den informationen vi söker har oftast en egen div class eller span class, dessa hittas genom att
            # inspect steams sidor med browsern. Måste finnas ett lättare, mera automatiserat sätt att göra detta?

            # Titteln
            g = i.span.text
            # Append titteln till den rätta listan
            gameTitle.append(g)

            # Sök spel ratings
            try:
                ratingContainer = i.find('span', class_='search_review_summary')[
                    'data-tooltip-html'].split('<br>')
                # Konverterar ratings till siffror från 2 till 10
                # Efter det, append rating till den rätta listan i form av en siffra
                if ratingContainer[0] == 'Overwhelmingly Positive':
                    rating.append('10')
                if ratingContainer[0] == 'Very Positive':
                    rating.append('9')
                if ratingContainer[0] == 'Positive':
                    rating.append('8')
                if ratingContainer[0] == 'Mostly Positive':
                    rating.append('7')
                if ratingContainer[0] == 'Mixed':
                    rating.append('6')
                if ratingContainer[0] == 'Mostly Negative':
                    rating.append('5')
                if ratingContainer[0] == 'Negative':
                    rating.append('4')
                if ratingContainer[0] == 'Very Negative':
                    rating.append('3')
                if ratingContainer[0] == 'Overwhelmingly Negative':
                    rating.append('2')
            # Ifall ett spel saknar rating sätter vi None som värde
            except:
                rating.append('None')

            # Rea procenten
            disc = i.find('div', class_='col search_discount responsive_secondrow').span.text
            # Append rea procenten till den rätta listan
            discountPercent.append(disc)

            # Rea pricet
            # Eftersom steam visar rea priset och normala priset tillsammans kastar vi bort originala priset med replace
            # Vi omformulerar också texten för att se finare ut
            discPr = i.find('div', class_='col search_price discounted responsive_secondrow').text.replace(
                ' ', '').replace('\n', '').replace('€', '€|')
            # Tar bort onödiga whitespaces och separators
            priceString1 = ''.join(discPr)
            priceTempList = priceString1.split('|')
            # Så tar vi bort det ursprungliga priset
            del priceTempList[::2]
            # Omformulering
            priceString2 = ''.join(priceTempList)
            # Append reapriset till den rätta listan
            discountPrice.append(priceString2)

            # Originala priset
            orig = i.find('div', class_='col search_price discounted responsive_secondrow').span.text
            # Append igen
            originalPrice.append(orig)

            # Release date
            release = i.find('div', class_='col search_released responsive_secondrow').text
            # Append igen
            releaseDate.append(release)
            
            # Vilka platformer som är stödda
            win = i.p.find('span', class_='platform_img win')
            mac = i.p.find('span', class_='platform_img mac')
            lin = i.find('span', class_='platform_img linux')

            # Konverterar datan till listor
            # Ändrar listorna vi hittade till string för att i nästa steg editera dem.
            # Kanske finns ett mera logiskt sätt?
            windowsList.append(win)
            macList.append(mac)
            linuxList.append(lin)
            windowsString = str(windowsList)
            macString = str(macList)
            linuxString = str(linuxList)

            # Ändra string till 1 (Stöder) eller 0 (stöder ej) för varje spel
            # Använder regex för att städa bort onödiga tecken -> Finare slutprodukt
            # Skulle ha villat använda re.sub() eftersom så många .replace efter varandra ser krångligt ut, men fick inte re.sub att fungera
            windowsSupportListCheck = windowsString.replace('[', '').replace(']', '').replace('\'', '').replace(
                '<span class=', '').replace('></span>', '').replace('platform_img win', '1').replace('None', '0')
            # Lägger den slutliga informationen till den rätta listan enligt separatorn
            windowsSupport = windowsSupportListCheck.split(', ')

            macSupportListCheck = macString.replace('[', '').replace(']', '').replace('\'', '').replace(
                '<span class=', '').replace('></span>', '').replace('platform_img mac', '1').replace('None', '0')
            # Lägger den slutliga informationen till den rätta listan enligt separatorn
            macSupport = macSupportListCheck.split(', ')

            linuxSupportListCheck = linuxString.replace('[', '').replace(']', '').replace('\'', '').replace(
                '<span class=', '').replace('></span>', '').replace('platform_img linux', '1').replace('None', '0')
            # Lägger den slutliga informationen till den rätta listan enligt separatorn
            linuxSupport = linuxSupportListCheck.split(', ')

            # Hur många ratings har spelet
            try:
                reviews = i.find('span', class_='search_review_summary')['data-tooltip-html']
                # Städar bort onödig text
                reviews = reviews.replace(' user reviews ', '|')
                # Appendar allting till en temp lista
                reviewsListRaw.append(reviews)
                reviewsString = ''.join(reviewsListRaw)
                # Städar bort allting förrutom siffror
                reviewsString = re.sub(r'(<br>\d+%)', '', reviewsString)
                reviewsString = re.sub(r"[a-zA-Z\s\.',-]", '', reviewsString)
                # Omformulerar med hjälp av | separatorn vi lagt till tidigare
                reviewsList = reviewsString.split('|')
                # Får för någon orsak en extra value, städar bort den
                del reviewsList[-1]

            # 0 betyder att spelet inte har ratings
            except:
                reviewsString = reviewsString + '0|'
                # Samma som tidigare, append till listan och städa onödigt bort
                reviewsList.append('0')
                reviewsListRaw.append('<br>00% of the 0|')

            # Datumet och tiden då scrapen har gjorts
            # datetime.now() en bra tool för att få datumet och tiden då koden körs
            dateTimeNow = datetime.now()

            # Omformaterar datumet
            todaysDateString = dateTimeNow.strftime('%d/%m/%Y %H:%M:%S')
            # You guessed it, append till listan :)
            scrapeDate.append(todaysDateString)

# Vi skapar en Dataframe genom att kombinera alla listor vi just gjort 
# Namnger columnerna med sina rätta namn (Valde att namnge dem på Engelska istället för Svenska, because that's how i roll)
df = pd.DataFrame({'Title': gameTitle, 'Rating': rating, 'Discount': discountPercent, 'Discounted Price': discountPrice, 'Original Price': originalPrice,
                             'Release date': releaseDate, 'Reviews': reviewsList, 'Windows support': windowsSupport, 'Mac Support': macSupport, 'Linux Support': linuxSupport, 'Date scraped': scrapeDate})

# Kontrolera ifall det redan finns en csv fil. Om det inte finns, skapar programmet en ny fil.
if os.path.exists('C:/Users/nikla/OneDrive - Arcada/steamScraperCSV.csv') == False:
    # € märket är svårt för python, måste därför skilt definierna encoding till utf-8-sig
    df.to_csv('C:/Users/nikla/OneDrive - Arcada/steamScraperCSV.csv', index=False, encoding='utf-8-sig')

# Ifall det redan finns en fil med samma namn skriver vi över den med en ny
else:
    with open('C:/Users/nikla/OneDrive - Arcada/steamScraperCSV.csv', 'r+', encoding='utf-8') as steamScraperFile:
        df.to_csv(steamScraperFile, index=False, encoding='utf-8-sig')

# Koden gör som instruktionerna vill, men det känns som om en stor del kunde ha gjorts lättare och mera automatiserats. Kanske sen nästa projekt :)
# Slutprodukten har också en massa onödiga "" tecken som jag ville fixa, men tiden och intresse slutade mitt i. Koden fungerar ändå så det har inte så stor skillnad