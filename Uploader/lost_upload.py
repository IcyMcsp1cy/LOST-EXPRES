from pymongo import MongoClient
from gridfs import GridFS

class LostUploader():
    def __init__(self, uri, database):
        self.client = MongoClient(uri)
        self.database = self.client[database]
        self.radialvelocity = self.database['radialvelocity']
        self.one = GridFS(self.database, collection='one')
        self.two = GridFS(self.database, collection='two')

        self.radialvelocity.remove()

        for i in self.one.find(): # or fs.list()
            self.one.delete(i._id)
        for i in self.two.find(): # or fs.list()
            self.two.delete(i._id)

    def upload1D(self, filepath, filename):
        bucket = GridFS(self.database, collection='one')
        file = open(filepath, 'rb')
        return bucket.put(file, filename=filename)

    def upload2D(self, filepath, filename):
        bucket = GridFS(self.database, collection='two')
        file = open(filepath, 'rb')
        return bucket.put(file, filename=filename)

    def uploadRV(self, entry):
        rv = self.database['radialvelocity']
        
        rv.insert_one(
            entry
        )

    def uploadSet(self, filepath1D, filepath2D, entry):
        id1 = self.upload1D(filepath1D, entry['filename'])
        id2 = self.upload2D(filepath2D, entry['filename'])
        id3 = self.uploadRV(entry)
        return (id1, id2, id3)

    def readOne(self, id):
        bucket = GridFS(self.database, collection='one')
        print(bucket.get(id).read())


if __name__ == '__main__':
    uploader = LostUploader('mongodb+srv://Dev:dev@cluster0.odagz.mongodb.net/SolarExpres?retryWrites=true&w=majority',
        'lost')
    entry = {
        'FILENAME': '200912.1113',
        'MJD': 59105.7392,
        'V': 1204.23,
        'E_V': 12.182,
        'SNR': 447,
        'EXPTIME': 96.256,
        'PUBLIC': True,
    }

    tuple = uploader.uploadSet(
        '200912.1113.1d_spectrum.csv', 
        '200912.1113.2d_spectrum.csv', 
        entry
    )
    print(tuple)
    
