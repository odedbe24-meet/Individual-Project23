from flask import Flask, render_template, request, redirect, url_for, flash
from flask import session as login_session
import pyrebase
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'super-secret-key'
config = {
  "apiKey": "AIzaSyAHmj-4l3MxN-g6ktOroKmT5vZf8AHduC0",
  "authDomain": "musicrecommendation-774f0.firebaseapp.com",
  "projectId": "musicrecommendation-774f0",
  "storageBucket": "musicrecommendation-774f0.appspot.com",
  "messagingSenderId": "81496575435",
  "appId": "1:81496575435:web:331e8186c1667083993a4e",
  "measurementId": "G-0QML0F494G",
  "databaseURL": "https://musicrecommendation-774f0-default-rtdb.europe-west1.firebasedatabase.app/"
}
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

SPOTIPY_CLIENT_ID = 'e9f15f9072e3401cb369dae713e5c99b'
SPOTIPY_CLIENT_SECRET = 'b10935eeef79428ba3f22157df8ab74b'
SPOTIPY_REDIRECT_URI = 'http://localhost:5000/home'  
# scope = 'playlist-read-private playlist-read-collaborative playlist-modify-public'


sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID,
                                                          client_secret=SPOTIPY_CLIENT_SECRET))


#Code goes below here

@app.route("/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            login_session['user'] = auth.sign_in_with_email_and_password(email,password)
            return redirect(url_for("home"))

        except:
            return render_template("login.html")

    else:
        return render_template("login.html")



@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        username = request.form['username']
        try:
            login_session['user'] = auth.create_user_with_email_and_password(email,password)
            UID = login_session['user']['localId']
            user ={"email": email, "password":password, "username": username, "discovered" : 0, "recommneded": 0}
            db.child("Users").child(UID).set(user)
            
            return render_template("home.html")
        except:
            flash("Auth Error")
            print("Error Messege")
            return render_template("singup.html")
    else:
        return render_template("signup.html")

@app.route("/home", methods=['GET', 'POST'])
def home():
    if request. method == 'POST':
        print("good")
    else:
        total_discoverd = db.child("Discoverd").get().val()
        total_recommended = db.child("Recommended").get().val()
        return render_template("home.html", total_discoverd=total_discoverd, total_recommended=total_recommended)



@app.route("/give", methods=['GET', 'POST'])
def give():
    if request.method == "GET":
        # requests = db.child(request).get().val()
        print("------------------------------")
        print(db.child("Requests").get().val())
        print("------------------------------")
        reqs = db.child("Requests").get().val()
        return render_template("give.html", reqs=reqs)
    else:
        answer = request.form['answer']
        giver = db.child("Users").child(login_session['user']['localId']).child("username").get().val() 
        reqs = reqs = db.child("Requests").get().val()
        postID = request.form['ID']
        updated = {answer:giver}
        db.child("Requests").child(postID).child("Answers").update(updated)
        answers = db.child("Requests").child(postID).child("Answers").get().val()
        recommned = db.child("Users").child(login_session['user']["localId"]).child("recommneded").get().val()
        recommned = recommned +1
        temp = db.child("Recommended").get().val() +1
        db.child("Recommended").set(temp)
        temp = db.child("Discoverd").get().val() + 1
        db.child("Discoverd").set(temp)
        db.child("Users").child(login_session['user']["localId"]).child("recommneded").set(recommned)

        return render_template("give.html", reqs=reqs, answers=answers)
    






    
@app.route("/profile", methods=['GET', 'POST'])
def profile():
    if request.method == "GET":
        UID = login_session['user']["localId"]
        username = db.child('Users').child(UID).child("username").get().val()
        email = db.child('Users').child(UID).child("email").get().val()
        discoverd = db.child('Users').child(UID).child("discovered").get().val()
        recommneded = db.child('Users').child(UID).child("recommneded").get().val()
        
        return render_template("profile.html", username=username, email=email, disc=discoverd, recommneded=recommneded)






@app.route("/get", methods=['GET', 'POST'])
def get():
    if request.method == "GET":
        return render_template("get.html")
    else:
        title = request.form['title']
        body = request.form['body']
        UID = login_session['user']['localId']
        username = db.child('Users').child(UID).child('username').get().val()
        
        song_request = {"title": title, "body":body, "username":username, "UID":UID, "answers":{} }
        db.child("Requests").push(song_request)
        return redirect(url_for("home"))




@app.route("/ai", methods=['GET', 'POST'])
def ai():
    if request.method == "POST":
        num_of_results = 1
        search_word = request.form['search_word']
        results = sp.search(search_word, num_of_results, 0, "track")
        limit_of_songs = 20
        for i in range(num_of_results):
            print(results['tracks']['items'][i]['id'])
        recomendation = sp.recommendations(seed_tracks=[results['tracks']['items'][0]['id']],limit=limit_of_songs)
        updated = db.child("Users").child(login_session['user']['localId']).child("discovered").get().val()
        updated = updated + limit_of_songs
        db.child("Users").child(login_session['user']['localId']).child("discovered").set(updated)
        temp = db.child("Discoverd").get().val() + limit_of_songs
        db.child("Discoverd").set(temp)
        rec_name ={}
        rec_link =[]
        for track in recomendation['tracks']:
            song_name = track['name']
            artist_name = track['artists'][0]['name']
            track_id = track['id']
            spotify_link = "https://open.spotify.com/track/"+track_id
            print(spotify_link)
            rec_link.append(spotify_link)
            rec_name[song_name] =artist_name
        return render_template("ai.html", rec_name=rec_name, rec_link=rec_link)
    

    else:
        return render_template("ai.html")
    

@app.route("/logout", methods=['GET', 'POST'])
def logout():
    if(request.method == "POST"):
        flash("you are being logged out")
        login_session['user']= None
        auth.current_user = None
        return redirect(url_for("login"))
    else:
        return redirect(url_for("login"))


@app.route("/recommend", methods=['GET', 'POST'])
def recommned():
    if request.method == "GET":
        return render_template("recommend.html")
    else: 
        return redirect(url_for("home"))



#Code goes above here

if __name__ == '__main__':
    app.run(debug=True)


