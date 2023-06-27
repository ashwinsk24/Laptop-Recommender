from flask import Flask, request, render_template
import pickle
import random

laptop = pickle.load(open('model/usecases_list.pkl', 'rb'))
similarity = pickle.load(open('model/similarity.pkl', 'rb'))


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


@app.route("/", methods=['GET', 'POST'])
def home():
    usecase_list = laptop['usecases'].unique()

    # Select 4 random laptop indices from the dataset
    random_laptops = random.sample(list(laptop.index), 8)
    laptop_names = [laptop.loc[laptop_index, 'name']
                    for laptop_index in random_laptops]
    img_links = [laptop.loc[laptop_index, 'img_link']
                 for laptop_index in random_laptops]

    return render_template("index.html", laptop_names=laptop_names, img_links=img_links, usecase_list=usecase_list)


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
