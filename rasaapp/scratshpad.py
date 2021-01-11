import geonamescache

gc = geonamescache.GeonamesCache()
countries = gc.search_cities("aa")
print(countries)
for c in countries:
    print(c)