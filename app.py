import io
import os
from flask import Flask, request, jsonify, render_template
from keras.applications import ResNet50
from keras.preprocessing.image import img_to_array
from keras.applications import imagenet_utils
from keras.models import load_model
from PIL import Image
import numpy as np





app = Flask(__name__)

model = None
MODEL_PATH = './models/'
MODEL_FILE_NAME = 'ResNet_model_weights.h5'
#MODEL_FILE_NAME = 'MobileNet_model_weights.h5'
MODEL_CLASS_FILE_NAME = 'ResNet_classLabelMap.npy'
#MODEL_CLASS_FILE_NAME = 'MobileNet_classLabelMap.npy'
MODEL_CLASS_MAPP = {}

def retrieve_model():
    # load the pre-trained Keras model (here we are using a model
    # pre-trained on ImageNet and provided by Keras, but you can
    # substitute in your own networks just as easily)
    
    if not os.path.exists(MODEL_PATH):
        os.mkdir(MODEL_PATH)
        print("Directory " , MODEL_PATH ,  " Created ")
    else:    
        print("Directory " , MODEL_PATH ,  " already exists")
    
    modelFilePath = MODEL_PATH + MODEL_FILE_NAME

    dictPath = MODEL_PATH + MODEL_CLASS_FILE_NAME
    global MODEL_CLASS_MAPP
    MODEL_CLASS_MAPP = np.load(dictPath, allow_pickle=True).item()

    global model
    model = load_model(modelFilePath)
    #model = ResNet50(weights="imagenet")
    model._make_predict_function()
    



def prepare_image(image, target):
    # if the image mode is not RGB, convert it
    if image.mode != "RGB":
        image = image.convert("RGB")

    # resize the input image and preprocess it
    image = image.resize(target)
    image = img_to_array(image)
    image = np.expand_dims(image, axis=0)
    image = imagenet_utils.preprocess_input(image)

    # return the processed image
    return image

def model_predict(image, model):
    data = {"success": False, "Prediction": "None"}
    data["predictions"] = []

    preds = model.predict(image)
    
    for class_index in range(len(MODEL_CLASS_MAPP)):
        class_label = MODEL_CLASS_MAPP[class_index]
        r = {"Label": class_label, "Probability": float(preds[0][class_index])}
        data["predictions"].append(r) 
        pass

    prediction=np.argmax(preds,axis=1)
    data["Prediction"] = MODEL_CLASS_MAPP[prediction[0]]

    data["success"] = True


    #results = imagenet_utils.decode_predictions(preds)
    #data["predictions"] = []

    #for (imagenetID, label, prob) in results[0]:
    #            r = {"label": label, "probability": float(prob)}
    #            data["predictions"].append(r)

    #data["success"] = True
    
    return jsonify(data)



@app.route("/")
def index():
    return render_template('index.html', message="Hello Flask!")



@app.route("/predict", methods=["POST"])
def predict():    
    result = ""
    # ensure an image was properly uploaded to our endpoint
    if request.method == "POST":
        if request.files.get("image"):
            # read the image in PIL format
            image = request.files["image"].read()
            image = Image.open(io.BytesIO(image))

            # preprocess the image and prepare it for classification
            image = prepare_image(image, target=(224, 224))

            # classify the input image and then return prediction data
            
            result = model_predict(image, model)
                            
    # return the data dictionary as a JSON response
    return result


if __name__ == "__main__":

    print(("* Loading Keras model and Flask starting server..."
        "please wait until server has fully started"))
    retrieve_model()
    app.run()










