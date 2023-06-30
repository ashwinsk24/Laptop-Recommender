from flask import redirect, url_for
from flask import redirect, session, url_for
from functools import wraps
from flask import Flask, request, render_template
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
import pickle
import random

laptop = pickle.load(open('model/usecases_list.pkl', 'rb'))
similarity = pickle.load(open('model/similarity.pkl', 'rb'))


def authentication_required(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        if 'user' in session:
            return route_function(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrapper


def recommendmov(use):
    index = laptop[laptop['usecases'] == use].index[0]
    distances = sorted(
        list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_laptops = []
    printed_names = set()
    for i in distances[1:10]:
        row_index = i[0]
        name = laptop.iloc[row_index]['name']
        img_link = laptop.iloc[row_index]['img_link']
        price = laptop.iloc[row_index]['price']
        if name not in printed_names:
            printed_names.add(name)
            recommended_laptops.append(
                {'name': name, 'img_link': img_link, 'price': price})
    return recommended_laptops


app = Flask(__name__)

cred = credentials.Certificate('auth\laptoprec2023-firebase-adminsdk-gcd2b-298485398f.json')
firebase_admin.initialize_app(cred)

app.secret_key = 'cred'
@app.route("/protected", methods=['GET'])
@authentication_required
def protected():
    return "Protected route"


@app.route("/", methods=['GET', 'POST'])
def home():
    # Check if the user is authenticated
    user = None
    if 'user_id' in session:
        try:
            user = auth.get_user(session['user_id'])
        # User is authenticated, set authenticated to True in the template context
            authenticated = 'user_id' in session

        except auth.AuthError:
            # Handle error if user not found
            authenticated = False
    else:
        # User is not authenticated, set authenticated to False in the template context
        authenticated = False

    usecase_list = laptop['usecases'].unique()
    # Select 8 random laptop indices from the dataset
    random_laptops = random.sample(list(laptop.index), 8)
    laptop_names = [laptop.loc[laptop_index, 'name']
                    for laptop_index in random_laptops]
    img_links = [laptop.loc[laptop_index, 'img_link']
                 for laptop_index in random_laptops]

    return render_template("index.html", user=user, authenticated=authenticated, laptop_names=laptop_names, img_links=img_links, usecase_list=usecase_list)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth.create_user(email=email, password=password)
            # User registration successful
            session['user_id'] = user.uid
            return redirect('/')  # Redirect to index.html
        except firebase_admin.auth.EmailAlreadyExistsError:
            # Handle case where the email already exists
            return "Email already exists"
        except Exception as e:
            # Handle other registration errors
            return str(e)
    else:
        return render_template("register.html")


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth.get_user_by_email(email)
            # Authenticate the user
            # You can use user.uid or user.email to identify the authenticated user in your application
            session['user_id'] = user.uid
            return redirect('/')
        except firebase_admin.auth.UserNotFoundError:
            # Handle case where the user is not found
            return "User not found"
        except Exception as e:
            # Handle other login errors
            return str(e)
    else:
        return render_template("login.html")


@app.route("/favourites")
#@authentication_required
def favourites():
    if 'favourites' in session:
        favourites = session['favourites']
        laptop_details = []
        for laptop_name in favourites:
            laptop_data = laptop.loc[laptop['name'].str.lower() == laptop_name.lower()].iloc[0]
            laptop_details.append(laptop_data)
        return render_template("favourites.html", laptop_details=laptop_details)
    else:
        return render_template("favourites.html", laptop_details=[])

@app.route("/logout")
def logout():
    session.pop('user_id', None)
    return redirect('/')

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/product", methods=['GET', 'POST'])
def product():
    usecase_list = laptop['usecases'].unique()
    status = False

    if request.method == "POST":
        try:
            if request.form:
                laptop_name = request.form['laptop_name']
                # Retrieve laptop data by matching the laptop name
                laptop_data = laptop.loc[laptop['name'].str.lower(
                ) == laptop_name.lower()].iloc[0]
                if not laptop_data.empty:
                    img_link = laptop_data['img_link']
                    laptop_name = laptop_data['name']
                    price = laptop_data['price']
                    laptop_brand = laptop_data['laptop_brand']
                    description = laptop_data['tags']
                    status = True

                    return render_template("product.html", img_link=img_link, laptop_name=laptop_name, laptop_brand=laptop_brand, price=price, description=description, usecase_list=usecase_list, status=status)
                else:
                    # Handle case where laptop data is not found
                    error = {'error': 'Laptop not found'}
                    return render_template("product.html", error=error, usecase_list=usecase_list, status=status)

        except Exception as e:
            error = {'error': e}
            return render_template("product.html", error=error, usecase_list=usecase_list, status=status)

    return render_template("product.html", usecase_list=usecase_list, status=status)


@app.route("/recommend", methods=['GET', 'POST'])
def recommend():

    usecase_list = laptop['usecases'].unique()
    status = False

    if request.method == "POST":
        try:
            if request.form:
                usecase = request.form['usecases']
                recommended_laptops = recommendmov(usecase)
                laptop_names = [laptop['name']
                                for laptop in recommended_laptops]
                img_links = [laptop['img_link']
                             for laptop in recommended_laptops]
                prices = [laptop['price'] for laptop in recommended_laptops]
                status = True

                return render_template("prediction.html", laptop_names=laptop_names, img_links=img_links, usecase_list=usecase_list, status=status)

        except Exception as e:
            error = {'error': e}
            return render_template("prediction.html", error=error, usecase_list=usecase_list, status=status)

    else:
        return render_template("prediction.html", usecase_list=usecase_list, status=status)


if __name__ == '__main__':
    app.debug = True
    app.run()
