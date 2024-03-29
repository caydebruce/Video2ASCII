from PIL import Image, ImageOps, ImageEnhance
import cv2
import os
import imgkit
import shutil

# Turns a video frames into images
def video_to_images(video_path):
    os.mkdir('Images') # Place to store images from video
    video = cv2.VideoCapture(video_path) # import video
    fps = video.get(cv2.CAP_PROP_FPS) # Returns FPS of current video to use in ascii video
    success, image = video.read()
    counter = 1 # number of images
    while success:
        cv2.imwrite("Images/Image{0}.jpg".format(str(counter)), image) # creates image with increasing number
        success, image = video.read()
        counter += 1
    return fps, (counter - 1)

# Gets image from a path
def get_image(image_path):
    initial_image = Image.open(image_path) # opens first image
    w, h = initial_image.size # grabs dimensions
    initial_image = initial_image.resize((round(w*1.05),h)) # offset if for the difference in width in ascii
    return initial_image

# Pixelates a given image
def pixelate_image(image, final_w = 144):
    w, h = image.size # next three lines does necessary resizing
    final_h = int((h*final_w)/w)
    image = image.resize((final_w, final_h))
    # image = ImageEnhance.Brightness(image) # helps with the darkness of ascii backgrounds
    # image = image.enhance(1.5) # makes things look nicer
    return image

# Turns image into grayscle NOT black and white
def grayscale_image(image): 
    gs_image = ImageOps.grayscale(image)
    return gs_image

# Turns grayscale image into list of ascii characters
def convert_to_ascii(gs_image, ascii_chars = [" ",".",":","-","=","+","*","#","%","@","&"]):
    pixels = gs_image.getdata()
    ascii_image_list = [] # initializes final array
    for pixel in pixels:
        ascii_converted = int((pixel*len(ascii_chars))/265) # gets index into ascii_chars
        ascii_image_list.append(ascii_chars[ascii_converted]) # pixel brightness value into ascii char
    return ascii_image_list

# Gets list of color values from image
def get_color(image):
    pixels = image.getdata() # list of RGB values for each pixel
    return pixels

def print_ascii(ascii_chars, image, color, image_pos):
    file = open('HtmlImages/Html{0}.html'.format(str(image_pos)),"w")
    file.write("""
        <!DOCTYPE html>
        <html>
            <body style='background-color:black'>
            <pre style='display: inline-block; border-width: 4px 6px; border-color: black; border-style: solid; background-color: black; font-size: 32px; font-face: Montserrat; font-weight: bold; line-height:60%'>""")
    w, _h = image.size
    counter = 0
    for i in ascii_chars:
        color_hex_val = '%02x%02x%02x' % color[counter]
        counter += 1
        if (counter % w) != 0:
            file.write("<span style=\"color: #{0}\">{1}</span>".format(color_hex_val,i))
        else:
            file.write("<br />")
    file.write("""</pre></body>
            </html>""")
    file.close()

def main(video_path):   
    config = imgkit.config(wkhtmltoimage=r'wkhtmltoimage')
    ascii_chars = [" ",".",":","-","=","+","*","#","%","@","&"] # magic characters
    fps, number_images = video_to_images(video_path)

    os.mkdir('HtmlImages')
    os.mkdir('TextImages')

    for i in range(1,number_images + 1):
        image = get_image('Images/Image{0}.jpg'.format(str(i)))
        correct_size_image = pixelate_image(image)
        gs_image = grayscale_image(correct_size_image)
        converted_array = convert_to_ascii(gs_image, ascii_chars)
        color_array = get_color(correct_size_image)
        print_ascii(converted_array, correct_size_image, color_array, i)
        imgkit.from_file('HtmlImages/Html{0}.html'.format(str(i)), 'TextImages/Image{0}.jpg'.format(str(i)), config = config)
    
    res = Image.open('TextImages/Image1.jpg').size
    video = cv2.VideoWriter('final_video.mp4', cv2.VideoWriter_fourcc('m', 'p', '4', 'v'), int(fps), res)
    
    for j in range(1, number_images + 1):
        video.write(cv2.imread('TextImages/Image{0}.jpg'.format(str(j))))
    video.release()

    # Clean up
    # !!! Do not change these !!!
    shutil.rmtree('HtmlImages')
    shutil.rmtree('TextImages')
    shutil.rmtree('Images')

main(input("Please Type File Path: "))