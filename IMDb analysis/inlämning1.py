#!/usr/bin/env python3
import pandas as pd
import regex as re

def read_userData(data):
    # Uppgift 2: Lämnar bort den onödiga informationen
    data = data.drop(['User id', 'Zip code'], axis=1)

    # Uppg 3: Endast användare med yrket 'other' visas då man kallar variabeln occupation i main()
    occupation = data.loc[data['Occupation'] == 'other']
    occupation.set_index('Age', inplace=True)

    # Uppg 3: Endast Män över 40 listas då man kallar variabeln maleOver40 i main()
    maleOver40 = data.loc[(data['Gender'] == 'M') & (data['Age'] > 40)]
    maleOver40.set_index('Age', inplace=True)

    # Uppg 4: Söker alla med yrket 'writer' i 'Occupation' kolumnen, räknar sedan medelåldern (mean)
    writers = data.loc[data['Occupation'] == 'writer']
    # writers returnerar nu medelåldern för författare
    writers = writers['Age'].mean()

    # Ser finare ut utan index
    data.set_index('Age', inplace=True)

    # Returnerar variablerna till main() funktionen där de sedan kan printas
    return data, occupation, maleOver40, writers

def read_ratingData(data):
    # Uppgift 2: Grupperar ratings enligt film
    group = data.groupby('Movie id', as_index= True)

    # Uppgift 4: Räknar medelrating per film
    mean = group['Rating'].mean()
    # Söker fram de filmer med över 40 ratings
    ratingSize = group['Rating'].size()
    ratingSize = ratingSize.loc[group['Rating'].size() > 40]

    # Bästa medelrating för de med över 40 ratings -->
    # Merge mean listan med den kortare ratingSize listan för att putsa bort filmer med för få ratings
    top = pd.merge(ratingSize, mean, left_index=True, right_on="Movie id")
    top.columns = ['Number of ratings', 'Average rating']
    # Nu när endast filmer med > 40 ratings finns kvar kan vi sort dem och visa top 10
    top = top.sort_values(['Average rating'], ascending=False)
    top = top.head(10)

    # Returnerar variablerna till main() funktionen där de sedan kan printas
    return mean, top
    
def read_movieData(data):
    # Jag är lite osäker om denna del, det ser ut som om Video release date saknas för alla filmer. Jag behandlar i detta fall datumet 
    # inom parentes som Release date och det längre datumet som Video release date eftersom jag inte vill tro att de lagt till en extra
    # column i onödan. 

    # Uppgift 1: Fixar release date så den syns på rätt rad, 
    data['Video release date'] = data['Release date']
    data['Release date'] = data['Movie title'].str.extract(r'(\d+)')
    # Raderar årtalet från filmens namn (Gör det dock stegvis för att inte radera text inom parentes)
    data['Movie title'] = data['Movie title'].str.replace(r'(\d+)','')
    # Raderar bara parenteser utan text, eftersom vissa filmer har parentes i namnet
    data['Movie title'] = data['Movie title'].str.replace(r'\(\)','')
    
    return data

def combine_df(jobData):
    # Uppgift 5: Delar datan mellan män och kvinnor
    m = jobData.loc[(jobData['Gender'] == 'M')]
    f = jobData.loc[(jobData['Gender'] == 'F')]

    # Gruppera kön enligt yrke
    mGroup = m.groupby('Occupation')
    fGroup = f.groupby('Occupation')

    # Kollar hur många som jobbar var
    mJobs = mGroup['Gender'].size().astype(float)
    fJobs = fGroup['Gender'].size().astype(float)
    mTopJobs = mJobs.sort_values(ascending=False)
    fTopJobs = fJobs.sort_values(ascending=False)

    # Kombinerar infon för att jämföra yrken mellan män och kvinnor
    jobs = pd.concat([fTopJobs, mTopJobs], axis=1)
    jobs.columns = ['Females', 'Males']

    # Ta bort NaN
    jobs['Females'] = jobs['Females'].fillna(0)

    # Plussa för att få alla som jobbar med detta yrke
    jobs['All'] = jobs['Females'] + jobs['Males']

    # Dividera för att få andelen
    jobs['Ratio Male/Female'] = jobs['Males']/jobs['Females']

    return jobs
    
def main():
    # Läs datan och omformulera till en lättare form
    # Uppgift 1
    user = pd.read_csv("ml-100k/u.user", sep="|", header=None, encoding='latin-1')
    user.columns = ['User id', 'Age', 'Gender', 'Occupation', 'Zip code']

    rating = pd.read_csv("ml-100k/u.data", sep="\s+|\t+|\s+\t+|\t+\s+", header=None, encoding='latin-1', engine='python', dtype=int)
    rating.columns = ['User id', 'Movie id', 'Rating', 'Timestamp']

    movie = pd.read_csv("ml-100k/u.item", sep="|", header=None, usecols=range(5), encoding='latin-1')
    movie.columns = ['Movie id', 'Movie title', 'Release date', 'Video release date', 'IMDb url']

    # Alla variabler som önskades i uppgifterna 2 och 3 
    # behöver ändast editera print() is slutet av dokumentet för att se dem
    userData, occupation, maleOver40, writers = read_userData(user)
    mean, top = read_ratingData(rating)
    movieData = read_movieData(movie)

    # Uppgift 5 vanligaste yrken
    typicalOccupation = combine_df(userData)

    # Uppgift 5 Kombinera dataframes
    # den fixade u.item + u.data
    combined1 = pd.merge(rating, movieData)
    # Putsar bort 'onödig' information
    combined1 = combined1.drop(['Movie id', 'Timestamp', 'IMDb url'], axis=1)
    # Kombinera med u.user
    combinedFinal = pd.merge(combined1, user)

    # Uppgift 5 de snällaste och tuffaste
    group = combinedFinal.groupby('User id', as_index=False)
    # Räkna medeltal av ratings
    mean = group['Rating'].mean()
    mean = mean.sort_values(by='Rating', ascending=False)
    # Plocka snällaste (top) och tuffaste (bottom)
    top = mean.head(5)
    bottom = mean.tail(5)

    # Uppgift 5 Kombinera med user för att visa information om användaren
    userInfoTop = pd.merge(user,top)
    userInfoBottom = pd.merge(user,bottom)
    # Genom att kolla på informationen kan vågar jag påstå att varker kön eller yrke påverkar hur
    # snäll eller tuff en person är då det kommer till filmer. Den slutsats som man kanske kunde
    # dra är att yngre(13-21) människor ger bättre ratings än de äldre(21-32). Urvalet är dock för
    # litet för att dra säkra slutsatser, speciellt då det också förekommer ett undantag blad de 'snälla'


    # Byt variabelnamn för att printa svaren
    print(typicalOccupation)

if __name__ == "__main__":
    main()