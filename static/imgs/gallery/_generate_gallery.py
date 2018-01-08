import os
import exifread
from subprocess import call
import re

def _get_if_exist(data, key):
    if key in data:
        return data[key]

    return None

def get_date(tags):
    if 'EXIF DateTimeOriginal' in tags:
        raw_date = str(tags['EXIF DateTimeOriginal'])
        date = raw_date.split(" ")[0].replace(":","-") + "T" + raw_date.split(" ")[1] + "Z"
        return date

    return None

def get_size(tags):
    width = _get_if_exist(tags, 'EXIF ExifImageWidth')
    height = _get_if_exist(tags, 'EXIF ExifImageLength')
    if "Rotated 90" not in str(_get_if_exist(tags, 'Image Orientation')):
        size = "{0}x{1}".format(width,height)
    else:
        size = "{0}x{1}".format(height, width)
    return size

def _convert_to_degress(value):
    d = float(value.values[0].num) / float(value.values[0].den)
    m = float(value.values[1].num) / float(value.values[1].den)
    s = float(value.values[2].num) / float(value.values[2].den)

    return d + (m / 60.0) + (s / 3600.0)


def get_location(exif_data):
    lat = None
    lon = None
    array = None
    gps_latitude = _get_if_exist(exif_data, 'GPS GPSLatitude')
    gps_latitude_ref = _get_if_exist(exif_data, 'GPS GPSLatitudeRef')
    gps_longitude = _get_if_exist(exif_data, 'GPS GPSLongitude')
    gps_longitude_ref = _get_if_exist(exif_data, 'GPS GPSLongitudeRef')

    if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
        lat = _convert_to_degress(gps_latitude)
        if gps_latitude_ref.values[0] != 'N':
            lat = 0 - lat

        lon = _convert_to_degress(gps_longitude)
        if gps_longitude_ref.values[0] != 'E':
            lon = 0 - lon

        array = "[{0}, {1}]".format(lat,lon)


    return array

def get_title(exif_data):
    title = _get_if_exist(exif_data, 'Image ImageDescription')
    if title == 'None':
        return ''
    return title

def get_comment(exif_data):
    text = _get_if_exist(exif_data, 'Image XPComment')
    if not text is None:
        text.values = u"".join(map(chr, text.values))
        text.values = re.sub(r'\W+', '', text.values)
        return text.values
    else:
        return ""

def generate_file(img, folder):
    path = 'C:\\Users\\jmsav\\Documents\\Website\\live\\content\\gallery\\'
    directory = 'C:\\Users\\jmsav\\Documents\\Website\\live\\static\\imgs\\gallery\\'
    filename = img.split(".")[0] + ".md"
    if not os.path.exists(os.path.join(path,filename.lower())):

        with open(os.path.join(directory + folder,img),'rb') as img_file:
            tags = exifread.process_file(img_file)
        file =  "---\n"
        file += "title: '{0}'\n".format(get_title(tags))
        file += "draft: false\n"
        file += "path: " + folder + "/" + img + "\n"
        file += "description: '{0}'\n".format(get_comment(tags))
        file += "date: " + get_date(tags) + "\n"
        file += "location: {0}\n".format(get_location(tags))
        file += "size: {0}\n".format(get_size(tags))
        file += "catergory: {0}\n".format(folder[3:])
        file += "--- "

        
        with open(os.path.join(path,filename.lower()),'w') as temp_file:
            temp_file.write(file)

        call("convert {0}\\{2}\\{1} -resize 250 {0}\\thumbs\\{2}\\{1}".format(directory, img, folder), shell=True)


directory_in_str = 'C:\\Users\\jmsav\\Documents\\Website\\live\\static\\imgs\\gallery'
path_in_str = 'C:\\Users\\jmsav\\Documents\\Website\\live\\content\\gallery\\'
directory = os.fsencode(directory_in_str)

for file in os.listdir(directory):
    filename = os.fsdecode(file)
    if os.path.isdir(file):

        for child in os.listdir(os.fsencode(directory_in_str + "\\" + filename)):
            img_file = os.fsdecode(child)

            if not img_file == "thumbs":
                generate_file(img_file, filename)
            continue
    else:
        continue

