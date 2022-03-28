FROM jupyter/scipy-notebook:b418b67c225b
#FROM ubuntu:21.10
#FROM python:3.9.7
USER root
RUN apt-get update && apt-get install build-essential -y
RUN apt-get install build-essential cmake -y
RUN apt-get install libopenblas-dev liblapack-dev -y 
RUN apt-get install libx11-dev libgtk-3-dev -y
#RUN apt-get install python3 python3-dev python3-pip -y

USER $NB_UID
COPY . .
EXPOSE 8888 8000 8080

RUN pip3 install --no-cache-dir --upgrade -r requirements.txt
