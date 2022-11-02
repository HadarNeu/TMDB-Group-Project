#getting the modules we need:
#Flask in order to build our website
#api_conf is our module which includes api functions to the TMDB webside and MongoDB
#base64 is to convert the image data to a actual image
#internalservererror is the function which handles server exceptions
from flask import Flask, render_template, request
from flask import jsonify
from api_conf import *
from base64 import b64encode
from werkzeug.exceptions import InternalServerError

app = Flask(__name__)

#if we get an internal server error we print an error message on the screen
@app.errorhandler(InternalServerError)
def validation_failure(err):
  return jsonify({"ERROR NAME !!!":" ---> PLEASE,TRY AGAIN !!!"}),500

#if we go to our hosts ip address in pur browser, the program is started!
@app.route('/')
def index():
    return render_template('search.html')

#if we put about after our ip in the browser we get to the about page
@app.route('/about')
def about():
    return "About page"

#if we INSERT a movie name a search command is started in our mongo db
@app.route('/search',methods=['GET', 'POST'])
def load_insert_html():
    if request.method == 'POST': #if the request is post, get the movie id
        movie_name = request.form['name']
        imdb = mdb.get_movieid(movie_name)


    if mdb.find_data(): #if the file is found, display the image- decoding the data and making it to a displayable image
            binary_file = mdb.read_data()
            image = b64encode(binary_file).decode("utf-8")
            src = "data:image/gif;base64," + image
            return f'<center><img src={src} alt="{movie_name}" width="300" height="400"></center>'

    #if the file is not found, get it from tmdb website, and decode the data
    mdb.get_image_url(imdb)
    mdb.getPosterFile()
    mdb.insert_data()
    image = b64encode(mdb.f_bin).decode("utf-8")
    src = "data:image/gif;base64," + image
    return f'<center><img src={src} alt="{movie_name}" width="300" height="400"></center>'
    return render_template('search.html')

if __name__=="__main__":
    app.run(port=80,host="0.0.0.0")