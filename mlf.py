import requests, json, os, random, ast
import PIL
from PIL import Image

'''
var data = new FormData();
data.append("files", "<file_contents>", "<filename>");
//API endpoint for API sandbox 
xhr.open("POST", "https://sandbox.api.sap.com/ml/scenetextrecognition/scene-text-recognition");


//Available Security Schemes for productive API Endpoints
//OAuth 2.0

//sending request
xhr.send(data);

'''
#TODO get all available URLs as function options
#TODO set API key to json file

url = "https://sandbox.api.sap.com/ml/translation/translation"

fpath = "C:\\Users\\d063195\\Desktop\\apps\\app2\\application\\services\\auth.json"
ipath = "C:\\Users\\d063195\\Desktop\\_Kitbag\\Graphics\\"
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "APIKey": "Z2LpAUAf0SwOkfOCyCdIB7BNkbuLVXOS"
}

max_mega = 20
base_max = 1200

def get_oauth():
    oauth = "/oauth/token?grant_type=client_credentials"
    f = json.loads(open(fpath).read())
    auth_url = "%s%s" % (f["url"], oauth)
    data={
        'grant_type': 'authorization_code',
        'client_id': f["clientid"],
        'client_secret': f["clientsecret"]
    }
    return requests.post(auth_url, data=data).json()["access_token"]

def get_urls():
    '''
    Use the configuration JSON to get the URLs associated to the user. See AUTH.json in the source folder
    :return:
    '''

    urls = {}
    f = json.loads(open(fpath).read())
    furls = f["serviceurls"]
    for u in furls.keys():
        urls[u] = furls[u]
    print("%d API points available" % (len(urls)))

    return urls

def set_headers(oauth):
    return {"Authorization": "Bearer " + oauth}

def mlf_image_classifier(image_file):

    oauth = get_oauth()
    headers = set_headers(oauth)
    headers["Accept"] = "application/json"
    files = {"files": (image_file)}
    url = get_urls()["IMAGE_CLASSIFICATION_URL"]
    return requests.post(url, headers=headers, files=files)

def get_image():

    images = []
    for i in os.listdir(ipath):
        if i[-4:] == '.jpg':
            images.append(i)
    rand_image_path = "%s%s" % (ipath, images[random.randint(0,len(images)-1)])
    width, height, mega = get_image_pixels(rand_image_path)
    if mega > max_mega:
        image = get_resized_image(rand_image_path, width, height)
    else:
        image = open(rand_image_path, 'rb')
    return image

def get_image_pixels(image):
    '''
    :param image: image path
    :return: the width, height and mega pizels of the picture
    '''
    width, height = Image.open(image).size
    mega = (width * height)/1000000
    return width, height, mega

def get_resized_image(image, width, height):
    '''
    :param image: image path
    :param width:
    :param height:
    :return: resized image based on the greatest dimension in the image
    '''
    min_side = min(width, height)
    max_side = max(width, height)
    ratio = float(base_max / max_side)
    new_min = int(min_side*ratio)
    if height > width:
        height = base_max
        width = new_min
    else:
        width = base_max
        height = new_min
    i_image = Image.open(image).resize((width, height), PIL.Image.ANTIALIAS)
    i_image.save(image)

    return open(image, 'rb')

def translation():
    keys = ["sourceLangauge", "targetLanguages", "units"]
    unitkeys = ["value", "key", ]

    data = {
        "sourceLanguage": "en",
        "targetLanguages": [
            "de", "fr"
        ],
        "units": [
            {
                "value": "The shopping cart contains ten items.",
                "key": "CART_CONTENTS",
                "inlineElements": {
                    "ranges": [
                        {
                            "id": 1,
                            "begin": 27,
                            "end": 30
                        }
                    ],
                    "markers": [
                        {
                            "id": 2,
                            "position": 18,
                            "align": "left"
                        }
                    ]
                }
            }
        ]
    }
    r = requests.post(url, headers=headers, data=json.dumps(data))
    return r

def get_message(r):

    name = r["predictions"][0]["name"]
    timestamp = r["processedTime"]
    predictions = r["predictions"][0]["results"]
    message = "%s\n%s is %s with %f certainty. But could also be the following:" % (
    timestamp, name, predictions[0]["label"], predictions[0]["score"])
    i = 0
    for e in predictions:
        if i != 0:
            message = message + "\n%s with %f" % (e["label"], e["score"])
        i += 1

    return message


image = get_image()
r = mlf_image_classifier(image).json()
m = get_message(r)
print(m)
