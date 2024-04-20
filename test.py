from PyMovieDb import IMDB
imdb = IMDB()
res = imdb.search('2001: A Space Odyssey')
res2 = imdb.get_by_name('The Prestige')
print(res2)