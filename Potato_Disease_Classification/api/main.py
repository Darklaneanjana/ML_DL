import tensorflow as tf
from PIL import Image
from io import BytesIO
import numpy as np
from fastapi import FastAPI, File, UploadFile
from uvicorn import run
app = FastAPI()


model = tf.keras.models.load_model('/models/1')
class_names = ['Early blight', 'Late blight', 'Healthy']


def load_image(image_bytes):
    image = np.array(Image.open(BytesIO(image_bytes)))
    return image


@app.post('/predict')
async def predict(file: UploadFile = File(...)):

    image = load_image(await file.read())
    image = tf.expand_dims(image, 0)
    predictions = model.predict(image)

    return {'confidence': np.round( float(np.max(predictions)),4), 'class': class_names[np.argmax(predictions)]}


if __name__ == '__main__':
    run(app, port=8000, host='localhost')
