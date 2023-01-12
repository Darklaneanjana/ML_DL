from DeepLabModel import DeepLabModel
from PIL import Image
import numpy as np
import os

from starlette.responses import StreamingResponse
from fastapi import FastAPI, File, UploadFile
from uvicorn import run
from io import BytesIO
app = FastAPI()


# import class

_TARBALL_NAME = 'deeplab_model.tar.gz'
download_path = os.path.join(os.getcwd(), _TARBALL_NAME)
print('loading DeepLab model...')
MODEL = DeepLabModel(download_path)
print('model loaded successfully!')


def get_mask(original_im):

    resized_im, seg_map = MODEL.run(original_im)

    sky_class = 3  # sky class in the model
    sky_mask = np.zeros(seg_map.shape, dtype=np.int64)

    # filter sky
    sky_mask = np.where(seg_map == sky_class, 1, 0)

    return sky_mask


def load_image(image_bytes):
    image = Image.open(BytesIO(image_bytes))
    return image


@app.post('/sky-segment')
async def predict(file: UploadFile = File(...)):

    image = load_image(await file.read())
    sky_mask = get_mask(image)


    # convert 2d array to rgb image
    sky_image = np.zeros((sky_mask.shape[0], sky_mask.shape[1], 3), dtype=np.uint8)
    sky_image[:, :, 0] = sky_mask * 255
    sky_image[:, :, 1] = sky_mask * 255
    sky_image[:, :, 2] = sky_mask * 255

 
    img = Image.fromarray(sky_image, 'RGB')

    # save image with BytesIO
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    return StreamingResponse(BytesIO(img_byte_arr), media_type='image/png')


if __name__ == '__main__':
    run(app, port=8000, host='localhost')
