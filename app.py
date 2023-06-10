from flask import Flask, request, render_template
import pickle
import requests
import pandas as pd
from patsy import dmatrices

laptop = pickle.load(open('model/usecases_list.pkl', 'rb'))
similarity = pickle.load(open('model/similarity.pkl', 'rb'))


def recommendmovq(use):
    index = laptop[laptop['usecases'] == use].index[0]
    distances = sorted(
        list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    printed_names = set()
    recommended_laptop_name = []
    recommended_laptop_image = []
    for i in distances[1:500]:
        laptop_id = laptop.iloc[i[0]].laptop_id
        recommended_laptop_name.append(laptop.iloc[i[0]].name)

    return recommended_laptop_name

def recommendmov(use):
    index = laptop[laptop['usecases'] == use].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_laptop_name = []
    printed_names = set()
    for i in distances[1:6]:
        row_index = i[0]
        name = laptop.iloc[row_index]['name']
        if name not in printed_names:
            printed_names.add(name)
            recommended_laptop_name.append(name)
    return recommended_laptop_name

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/recommend", methods=['GET', 'POST'])
def recommend():

    usecase_list = laptop['usecases'].values
    status=False
    if request.method == "POST":
        try:
            if request.form:
                usecase = request.form['usecases']
                print(usecase)
                recommended_laptop_name = recommendmov(usecase)
                print(recommended_laptop_name)
                status = True
                
                return render_template("prediction.html", laptop_name=recommended_laptop_name, usecase_list=usecase_list, status = status)

        except Exception as e:
            error = {'error': e}
            return render_template("prediction.html",error = error, usecase_list=usecase_list, status = status)

    else:
        return render_template("prediction.html", usecase_list=usecase_list, status = status)


if __name__ == '__main__':
    app.debug = True
    app.run()
