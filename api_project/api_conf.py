#getting the modules we need:
#Requests module for our api requests from TMDB website
#IMDB module is to get the movie id for the TMDB search
#os is to get our API KEY saved as an environment variable on our local computer
#pymongo is the module which aloows us to communicate with our mongo db
#grid fs is a module which has data manipulation functions between flask and mongo db
import requests
import imdb
import os
import pymongo
import gridfs

class mvdb():

#The init function which hold our class data
    def __init__(self):
        self.KEY = os.environ.get('API_Key')  #getting the environment variable, our key, which we defined in our userdata
        self.url = f'http://api.themoviedb.org/3/configuration?api_key={self.KEY}'         #the configuration data request url:
        self.r = requests.get(self.url)
        self.config = self.r.json()
        self.base_url = self.config['images']['base_url']  #getting the structure for our base url for further requests
        self.sizes = self.config['images']['poster_sizes'][-1] #getting the size of the poster - we chose getting the biggest size
        self.IMG_PATTERN = 'http://api.themoviedb.org/3/movie/{imdbid}/images?api_key={KEY}'

#The function is recieving a movie name from the user (Happens in our html interface)
# and returns a movie id from the imdb database
    def get_movieid(self,movie_name):
        self.name = movie_name
        ia = imdb.Cinemagoer()
        search = ia.search_movie_advanced(self.name)

        #here we are making a new string with the tt letters (ex: 'tt:2446738')
        #in order to make a valid url.
        self.movieid = "tt" + str(search[0].movieID)
        return self.movieid

#this function gets the movieid and returns the image url
    def get_image_url(self,imdbid):
        self.imgurl = self.IMG_PATTERN.format(KEY=self.KEY,imdbid=imdbid) #enters the data into the image format
        r = requests.get(self.imgurl)
        self.api_response = r.json()

        #getting the first image name out of multiple possibilities. ex:23456789876543.jpg
        self.imgname = self.api_response['posters'][0]['file_path']
        self.url = "{0}{1}{2}".format(self.base_url, self.sizes, self.imgname)
        return self.url

#function that downloads the picture to a local file
    def getPosterFile(self):
        r = requests.get(self.url)
        filetype = r.headers['content-type'].split('/')[-1]

        filename = 'poster_{0}.{1}'.format(self.name, filetype)
        self.filename = filename

        #if the file does not exist we write the image into the file, thus downloading it locally
        with open(self.filename, 'wb') as w:
            w.write(r.content)
        return self.filename

#THE MONGO DB CLASS
class mongo(mvdb):
    """ DAL for mongo DB"""
    def __init__(self,ip,port,db_name,col_name):
        mvdb.__init__(self)
        self.myclient = pymongo.MongoClient(ip, port)
        self.db=self.myclient[db_name]
        self.col=self.db[col_name]

#function that inserts the poster (local file as filename) after downloading it, to the DB
    def insert_data(self):
        fs = gridfs.GridFS(self.db)
        with open(self.filename, 'rb') as read_file:
           file_bin = read_file.read()
           self.f_bin = file_bin
        file_id = fs.put(file_bin, filename=f"{self.movieid}")
        return file_id

#function that searches whether a poster exists in our DB
    def find_data(self):
        result = self.col.find_one({"filename": self.movieid})
        if result == None:
            return False
        self.objid = result['_id']
        return self.objid

#function that calls the find_data function and searches for a file in the db, and if exists- deletes it.
    def delete_data(self):
        result= mongo.find_data(self)
        if result != False:
            self.col.delete_one({"_id": self.objid})
        return

#function that pulls the file's content
    def read_data(self):
        fs = gridfs.GridFS(self.db)
        result = fs.find_one({"filename": self.movieid})
        image = result.read()
        return image


    """
    test module
    """
db_name="mydatabase"
col_name="fs.files"
ip='db-movie'
port=27017
mdb=mongo(ip,port,db_name,col_name)



