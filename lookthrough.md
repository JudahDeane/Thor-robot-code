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




