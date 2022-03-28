# 

FROM ubuntu:21.10
RUN apt-get update && apt-get install -y python3.9 python3.9-dev
# RUN apt-get -y install python3-pip

# RUN apt-get install python3 python3-dev python3-pip -y
# FROM python:3.9.7



RUN apt-get update && apt-get install build-essential -y
RUN apt-get install build-essential cmake -y
RUN apt-get install libopenblas-dev liblapack-dev -y 
RUN apt-get install libx11-dev libgtk-3-dev -y


# RUN apt-get update
# RUN apt-get install ffmpeg libsm6 libxext6  -y
# RUN apt-get install -y libgl1-mesa-dev
#-------------------------------------------------------
# RUN  apt-get install pkg-config
# RUN  apt-get install libgtk2.0-dev -y
# RUN pip uninstall opencv-python
# pip uninstall opencv-python-headless
# RUN apt-get -y install python3-pip
#--------------------------------------------------------
WORKDIR /code

#----------------------------------
#RUN apt-get update
# RUN apt install -y libgl1-mesa-glx
#---------------------------------------------
RUN apt-get -y install python3-pip
COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
# RUN pip uninstall PyQt5
# RUN pip install opencv-python

COPY ./app /code/app
RUN mkdir -p /output_files
CMD ["uvicorn", "app.detect:app", "--host", "0.0.0.0", "--port", "8080"]

