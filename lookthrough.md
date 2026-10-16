This is a document documenting all the bugs and errors I have found in my code and what I did to fix them


GOAL
to make a  hand tracking algorithim that will track your hands with 2 cameras in 3d and create a 3d diagram to contain them then translate that into different modes for the robot to react to. also mabey just track anything with a special symbol on it.

DIFFERNT MODES.
Sisscors paper rock
controling with hand
talking to it mabey through an ai model


GETTING HAND TRACKING DATA INTO ANOTHER PROCCESES

Idea 1 
reading and writing from a text file

Problem
it would be way to slow

Idea 2
use shared ram (very High speed storage) to communicate between different procceses 

affter many iterations of trying I got it working









BLENDER TEST


GOAL
so what I an trying to do is djsplay the a hand based on the points from the handtracking program to get a good visual.

GETING DATA IN FROM THE HAND TRACKING BLENDER

Idea 1
I was gonna run the script from out side of belnder to modifiy it.

Problem
you cant use scripts from outside of blender modify things inside of blender

Idea 2
run the script inisde of blenders built in scripting and use a while loop to update from the sharded memory

problem
if you run a while in blender it will freeze the main part of it and only run the script which means that it would be ussless

Idea 3
use a built in feature in blender to run a script every frame which I connect to shareded memory Which works

USING THE DATA TO MOVE OBJECTS

Idea 1
use a for loop for the length of coords then just apply the location of the points from -50 to positive 50 

It works lets go first Idea works


GETTING LIKE AN AI THING

TALKING 

GOAL
I am trying to get the robot to respond to me and talk back to me 

Idea 1
use the tts module called pyttsx3 to read out text to talk to the user

problem
when I run very basic code to just test it it breaks and displays and error with the librarys

Idea 2 
use a different libray called piper which creates a file and then plays it with winsound a built in thing

this works

GETTING AN AI MODEL TO TALK TO

Idea 1
getting a built in ollama model to send requests to with python

problem
the model needs like 32 gb of ram and i still need to run all my other stuff

Idea 2 
find a cheaper model to run on ollama

problem
finding another model is difficult so i just went back to Idea 1 

Idea 1 worked

I used an ollama api with python 


VOICE RECOGNITION

idea 1 
copy the code from a previous project

problem
the code only works with the other stuff i dont need

I fixed the code and found out why it was not working so now it does


so now the speech rocgonition goes into the ai which feeds into the piper module to create audio to play 
the average time to respond is about like 5 seconds ish 



MOVING THE ROBOT

Goal
I want to be able to control the robot through a python script

Idea 1 
use a python script that i can start in windows

issue is that i cant run the script from windows directly i have to run it through ubuntu
 









