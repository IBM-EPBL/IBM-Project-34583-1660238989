import os
import urllib
import uuid

import flask
from flask import Flask, render_template, request, send_file
from PIL import Image
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array, load_img

# create a flask object
app = Flask(__name__)

# load the model
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model = load_model(os.path.join(BASE_DIR, 'model.hdf5'))

# create file extension test function
ALLOWED_EXT = set(['jpg', 'jpeg', 'png', 'jfif'])


def allowed_file(filename):
    '''
    check the file fits the allowed extensions.
    '''
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXT







----------------------x----------------------------------------------------------------






classes = ['Marssonina leaf spot', '1', '3', '4', '5', '6', 'apple Black_rot', '8', '9', '10']


# define the predict function
def predict(filename, model):
    ''' Get a file and provide prediction
    ARGS:
        filename - the file to be uploaded to the route
        model - model file to predict with

    Returns:
        class_result, array, possible classes
        prob_result, array, the probability to fit each class
    '''
    img = load_img(filename, target_size=(32, 32))
    img = img_to_array(img)
    img = img.reshape(1, 32, 32, 3)

    img = img.astype('float32')
    img = img/255.0
    result = model.predict(img)

    dict_result = {}
    for i in range(10):
        dict_result[result[0][i]] = classes[i]

    res = result[0]
    res.sort()
    res = res[::-1]
    prob = res[:3]

    prob_result = []
    class_result = []
    for i in range(3):
        prob_result.append((prob[i]*100).round(2))
        class_result.append(dict_result[prob[i]])

    return class_result, prob_result


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/success', methods=['GET', 'POST'])
def success():
    error = ''
    target_img = os.path.join(os.getcwd(), 'static/images')
    if request.method == 'POST':
        if(request.form):
            link = request.form.get('link')
            try:
                resource = urllib.request.urlopen(link)
                unique_filename = str(uuid.uuid4())
                filename = unique_filename+".jpg"
                img_path = os.path.join(target_img, filename)
                output = open(img_path, "wb")
                output.write(resource.read())
                output.close()
                img = filename

                class_result, prob_result = predict(img_path, model)

                predictions = {
                    "class1": class_result[0],
                    "class2": class_result[1],
                    "class3": class_result[2],
                    "prob1": prob_result[0],
                    "prob2": prob_result[1],
                    "prob3": prob_result[2],
                }

            except Exception as e:
                print(str(e))
                error = 'This image from this site is not accesible or inappropriate input'

            if(len(error) == 0):
                return render_template('success.html', img=img, predictions=predictions)
            else:
                return render_template('index.html', error=error)

        elif (request.files):
            file = request.files['file']
            if file and allowed_file(file.filename):
                file.save(os.path.join(target_img, file.filename))
                img_path = os.path.join(target_img, file.filename)
                img = file.filename

                class_result, prob_result = predict(img_path, model)

                predictions = {
                    "class1": class_result[0],
                    "class2": class_result[1],
                    "class3": class_result[2],
                    "prob1": prob_result[0],
                    "prob2": prob_result[1],
                    "prob3": prob_result[2],
                }

            else:
                error = "Please upload images of jpg , jpeg and png extension only"

            if(len(error) == 0):
                return render_template('success.html', img=img, predictions=predictions)
            else:
                return render_template('index.html', error=error)

    else:
        return render_template('index.html')


# @app.route('/rec', methods=['GET', 'POST'])
# def rec():
#     return render_template("rec.html")


if __name__ == "__main__":
    app.run(debug=True)
