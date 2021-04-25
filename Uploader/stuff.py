from pymongo import MongoClient
from gridfs import GridFS

client = MongoClient('mongodb+srv://Dev:dev@cluster0.odagz.mongodb.net/SolarExpres?retryWrites=true&w=majority')

solar = client['SolarExpres']
fs = GridFS(solar)
fs_files = solar.fs.files
lost = client['lost']
id1 = fs_files.find_one({'filetype':'1d'})
id2 = fs_files.find_one({'filetype':'2d'})
one = GridFS(lost, collection='one')
two = GridFS(lost, collection='two')

entries = list(one.find())
for entry in entries:
    one.delete(entry._id)

entries = list(two.find())
for entry in entries:
    two.delete(entry._id)

# rvs = list(solar['radialvelocity'].find())

# rvi = lost['radialvelocity']

# rvi.insert_many(rvs)
# print('rvs done')
print(id1['_id'])
f1 = fs.get(id1['_id'])
d1 = one.put(f1, filename='200912.1113')
print('one done')
f2 = fs.get(id2['_id'])
d2 = two.put(f2, filename='200912.1113')
print('two done')

