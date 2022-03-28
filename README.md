# Physical Distance Detector

**API implementation without jupyter works. However API implementation with jupyter executes everything but is not accessible when the api is initiated from the dockerized jupyter.**

_**Nevertheless, I have provided the HTML file of the jupyter notebook.**_

## Installation steps for executinng API implementation without jupyter:


Run the following steps:

- Step 1: Change the directory ```ApiImplentationWithoutJupyter``` in your localhost.

- Step 2: Build the docker image
```
docker build -t PDDimage . 
```
- Step 3: Run the container
```
docker run -d --name pddimage1 -p 8080:8080 --mount type=bind,src="${pwd}"/output_files,target=/code/output_files PDDimage 

```
- Step 4: Run the following command abd look for  the message 'Application startup complete.'
```
docker logs pddimage1 
```

- Step 5: Go to the following address. (Other localhost address does not work.)

```
http://localhost:8080/docs 
```

-  Click on Try Out under the upload file
-  Upload any video file, I have given one in input files folder.
-  The video will be saved under ApiImplementationWithoutJupyter/output_files in your local system


## Installation steps for executing API implementation with jupyter:



Run the following commands

- Step 1: Change the directory ```ApiImplentationWithJupyter``` in your localhost 

- Step 2  Build the docker image
```
docker build -t PDDJupyterimage  . 
```
- Step 3: Run the container
```
docker run -d --name pddimage2 -p 8080:8080 --mount type=bind,src="${pwd}"/output_files,target=/output_files PDDJupyterimage  

```
- Step 4: Check the message by running the following command. Go to the link provided and provide the given token  for accessing the jupyter lab

```
docker logs pddimage2 
```

- Step 5: Execute each cell till you reach the run() function cell. Here it will open the API. However, I am not able to access it. Any suggestions will be helpful. If works follow the procedure.
  
-  Click on Try Out under the upload file
-  Upload any video file, I have given one in input files folder.
-  The video will be saved under ApiImplementationWithJupyter/output_files in your local system


## Improving accuracy:

- Use larger Yolo model.
- Use minimum frames to skip such that detection will run frequently. 
	- videdetect() --> set skip_frames =10 or 20

