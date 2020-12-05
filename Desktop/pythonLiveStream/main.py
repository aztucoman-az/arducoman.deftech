import numpy as np
import face_recognition as fr
from tkinter import *
import tkinter as tk
from imutils.video import VideoStream
from imutils.video import FPS
import argparse
import imutils
import time
import cv2

color = {"nero": "#252726","orange":"#FF8700",
         "darkorange":"#FE6101"}

Pencere = Tk()
Pencere.configure(background= 'blue')
Pencere.title("Gui")
Pencere.geometry("1200x800+350+350")
Pencere.resizable(False,False)
Pencere.minsize(100,100)
Pencere.state("iconic")



#frame = tk.Frame(root)
def webcamtemasi():
    cap = cv2.VideoCapture(0)
    bruno_image = fr.load_image_file("m2.jpg")
    bruno_face_encoding = fr.face_encodings(bruno_image)[0]
    known_face_encondings = [bruno_face_encoding]
    known_face_names = ["Known"]
    while True:
        ret, frame = cap.read()

        rgb_frame = frame[:, :, ::-1]

        face_locations = fr.face_locations(rgb_frame)
        face_encodings = fr.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = fr.compare_faces(known_face_encondings, face_encoding)
            name = "Unknown"
            face_distances = fr.face_distance(known_face_encondings, face_encoding)

            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

                cv2.rectangle(frame, (left, top), (right, bottom), (68, 255, 0), 2)

                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (68, 255, 0), cv2.FILLED)
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
            else:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        cv2.imshow('Webcam', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def objedetention():
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--prototxt", required=True,
                    help="path to Caffe 'deploy' prototxt file")
    ap.add_argument("-m", "--model", required=True,
                    help="path to Caffe pre-trained model")
    ap.add_argument("-c", "--confidence", type=float, default=0.2,
                    help="minimum probability to filter weak detections")
    args = vars(ap.parse_args())

    # initialize the list of class labels MobileNet SSD was trained to
    # detect, then generate a set of bounding box colors for each class
    CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
               "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
               "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
               "sofa", "train", "tvmonitor"]
    COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

    # load our serialized model from disk
    print("[INFO] loading model...")
    net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

    # initialize the video stream, allow the cammera sensor to warmup,
    # and initialize the FPS counter
    print("[INFO] starting video stream...")
    vs = VideoStream(src=0).start()
    time.sleep(2.0)
    fps = FPS().start()

    # loop over the frames from the video stream
    while True:
        # grab the frame from the threaded video stream and resize it
        # to have a maximum width of 400 pixels
        frame = vs.read()
        frame = imutils.resize(frame, width=400)

        # grab the frame dimensions and convert it to a blob
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
                                     0.007843, (300, 300), 127.5)

        # pass the blob through the network and obtain the detections and
        # predictions
        net.setInput(blob)
        detections = net.forward()

        # loop over the detections
        for i in np.arange(0, detections.shape[2]):
            # extract the confidence (i.e., probability) associated with
            # the prediction
            confidence = detections[0, 0, i, 2]

            # filter out weak detections by ensuring the `confidence` is
            # greater than the minimum confidence
            if confidence > args["confidence"]:
                # extract the index of the class label from the
                # `detections`, then compute the (x, y)-coordinates of
                # the bounding box for the object
                idx = int(detections[0, 0, i, 1])
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")

                # draw the prediction on the frame
                label = "{}: {:.2f}%".format(CLASSES[idx],
                                             confidence * 100)
                cv2.rectangle(frame, (startX, startY), (endX, endY),
                              COLORS[idx], 2)
                y = startY - 15 if startY - 15 > 15 else startY + 15
                cv2.putText(frame, label, (startX, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)

        # show the output frame
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

        # update the FPS counter
        fps.update()

    # stop the timer and display FPS information
    fps.stop()
    print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

    # do a bit of cleanup
    cv2.destroyAllWindows()
    vs.stop()


f1 = Frame(Pencere,width = 950, height =1200,bg = 'white')

f1.pack(side=RIGHT)
# Camera
img = PhotoImage(file ='/home/rafael/Desktop/pythonLiveStream/icon camera.png')
B = tk.Button(image= img ,text ="",command= webcamtemasi,height = 30, width = 150 ,bg = 'blue')
B.pack(padx =0, pady= 20)

#System Info
img2 = PhotoImage(file = '/home/rafael/Desktop/pythonLiveStream/icon info.png')
B2 = tk.Button(image= img2 ,text ="",command = objedetention ,height = 30, width = 150 ,bg = 'blue')
B2.pack(padx =0, pady= 25)

#Controller
img3 = PhotoImage(file = '/home/rafael/Desktop/pythonLiveStream/icon controller.png')
B3 = tk.Button(image= img3 ,text ="",height = 30, width = 150 ,bg = 'blue')
B3.pack(padx =0, pady= 25)

# MAP
img4 = PhotoImage(file = '/home/rafael/Desktop/pythonLiveStream/icon map.png')
B4 = tk.Button(image= img4 ,text ="",height = 30, width = 150 ,bg = 'blue')
B4.pack(padx =0, pady= 25)

# Support
img6 = PhotoImage(file = '/home/rafael/Desktop/pythonLiveStream/icon support.png')
B6 = tk.Button(image= img6 ,text ="",height = 30, width = 150 ,bg = 'blue')
B6.pack(padx =0, pady= 25)

# Setting
img5 = PhotoImage(file = '/home/rafael/Desktop/pythonLiveStream/icon settings.png')
B5 = tk.Button(image= img5 ,text ="",height = 30, width = 150 ,bg = 'blue')
B5.pack(padx =0, pady= 25)


#Pencere.maxsize()
mainloop()

#System Camera Info Control Settings