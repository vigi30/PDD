import torch
import os
# import cv2
import numpy as np
import math
import time
import shutil
from fastapi import FastAPI,File, UploadFile
import uvicorn
from PIL import Image
import dlib
from app.utils_detect import get_coordinates,get_distance,get_violated_distance_people_test,get_centroid,detect,draw_arrows


import cv2




# This part of code will download the model weights and skeleton of the Yolov5{s/m/l}.
# cls = 0 represents the person class which will make sure only the person object is detecteda and others are discarded.
# conf_thresh  = Minimum probability of the detected objects
# iou_thresh - Minimum threshold for IOU


# You can change this to yolov5s,yolov5m,yolov5l which signifies different model configuration 

def get_model(cls =0, conf_thresh=0.30,iou_thresh=0.30):
    dev = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    # model = torch.hub.load('ultralytics/yolov5', 'yolov5s').to(dev) # force_reload=True
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s',force_reload=True).to(dev)
    model.classes = cls #person
    model.conf = conf_thresh
    model.iou = iou_thresh
    # filename
    return model



#intializing the fast api object
app = FastAPI()


# The endpoint should accept a video via the body of a POST request (video can be small to circumvent large video issues)
# When the file is uploaded, the 'create_upload_file' function will be called first as this is our endpoint. This function will load the model, saves the uploaded file, and calls the videodetect function compute the PDD.
@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile= File(...)):
    model = get_model()
    folder_name = 'uploaded_files'
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
    temp_file = await _save_file_to_disk(file, path=folder_name, save_as=file.filename)
    detect_info,centroids,violated_people = await videodetect(model,temp_file,file.filename)
    return {'detection_objects':detect_info, 'centroids':centroids, 'violated_people_pair' : violated_people}
    # return {"filename": file.filename}



#I am storing the uploaded file into the local storage under uploaded_files folder
async def _save_file_to_disk(uploaded_file, path=".", save_as="default"):
    # extension = os.path.splitext(uploaded_file.filename)[-1]
    temp_file = os.path.join(path, save_as)
    with open(temp_file, "wb") as buffer:
        shutil.copyfileobj(uploaded_file.file, buffer)
    return temp_file


# Takes the uploaded file (filename) and computes PDD and saves the processed video with saving_file_name under the folder output_files

async def videodetect(model,filename, saving_file_name):

    '''
    In order to reduce the time and memory consumption as well as flickering of the deteted object, I used detection once every 50 frames (skip_frames) 
     and in between used object tracking algorithm from dlib library.  

    To use only detection algorithm, then, assign isTracking to False
    
    '''

    filepath = os.path.join(filename)
    cap = cv2.VideoCapture(filepath)
    if cap.isOpened() ==False:
        print("Error in opening up the file")
    
    if not os.path.exists('output_files'):
        os.mkdir('output_files')
    
    #stores all the coordinates, centroids and violated people of all the frames in the video.    
    detection_objects,all_centroids, all_violates = [],[],[]
    fourcc = cv2.VideoWriter_fourcc('X','V','I','D')
    save_file_path = os.path.join('output_files', saving_file_name)
    writer = cv2.VideoWriter(save_file_path, fourcc, 25,( int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),   int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))
    
    start = time.time()
    num_frames = 0
    skip_frames =50
    while cap.isOpened():
        
        ret, frame = cap.read()
        if ret:
            # Need to convert the image to RGB format as dlib accepts only RGB format
            RGBframe = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # For every N frames we will use detection algorithm
            if num_frames % skip_frames ==0:
                
                detect_info = detect(model, RGBframe)
                trackers = []
                 # Each detected object needs a tracker object which helps in tracking that object for the following frames 
                for object in detect_info:
                    
                    tracker = dlib.correlation_tracker()
                    rect = dlib.rectangle(object[0],object[1],object[2],object[3])
                    tracker.start_track(RGBframe, rect)
                    trackers.append(tracker)
                    # frame = cv2.rectangle(frame, (object[0],object[1]), (object[2],object[3]),(0, 255, 0), 2)
                
                # computing the distance between the objects and identifying the violated people in a frame
                centroids = get_centroid(detect_info)
                violated_people = get_violated_distance_people_test(centroids)
                frame = draw_arrows(frame, detect_info, centroids, violated_people)
                
                detection_objects.append(detect_info)
                all_centroids.append(centroids)
                all_violates.append(violated_people)
            else:

                # this part of code only uses object tracking, where each tracker (detected object) postion is updated based KCF tracking algorithm
                detect_info = []
                
                for tracker in trackers:

                    tracker.update(RGBframe)
                    pos = tracker.get_position()
                    startX = int(pos.left())
                    startY = int(pos.top())
                    endX = int(pos.right())
                    endY = int(pos.bottom())
                    detect_info.append((startX, startY, endX, endY))
                    # frame = cv2.rectangle(frame, (startX, startY), (endX, endY),(0, 255, 0), 2)

                # computing the distance between the objects and identifying the violated people in a frame
                centroids = get_centroid(detect_info)
                violated_people = get_violated_distance_people_test(centroids)
                frame = draw_arrows(frame, detect_info, centroids, violated_people)

                detection_objects.append(detect_info)
                all_centroids.append(centroids)
                all_violates.append(violated_people)
            
            # try:
            #     cv2.imshow('Frame', frame)
            #     if cv2.waitKey(25) & 0xFF == ord('q'):
            #         break
            # except:
            #     pass
            #     # print("cv2 not working")
            # finally:
            writer.write(frame)
            num_frames += 1
                
           
        else:
            # print("Not working")
            break

    end = time.time()
    seconds = end - start
    print("Time taken : {0} seconds".format(seconds))
    # Calculate frames per second
    fps = num_frames / seconds
    print("Estimated frames per second : {0}".format(fps))
    print(f"Total number of frames processed: {num_frames}")
    cap.release()
    writer.release()
    # try:
    #     cv2.destroyAllWindows()
    # except:
    #     pass


    return (detection_objects,all_centroids,all_violates)
# if __name__== "__main__":
# #     # videodetect()
#     uvicorn.run(app, host='0.0.0.0', port=8000)


