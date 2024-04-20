from imdbmovies import IMDB
imdb = IMDB()
res = imdb.get_by_name('the prestige')

print(res)
import movieposters as mp
poster_link = mp.get_poster('joker (2019)')
print(poster_link)