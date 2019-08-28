# Wee Archie LED Animation Server

This is a simple Flask web server which will allow users to queue animations on
an Adafruit LED backpack when run on a Raspberry Pi with one attached.

## Running the server

`virtualenv` is used to configure the Python environment, tested with Python
3.4.2 and up (not on Windows). To create a new environment:

`virtualenv .` in this directory

`bin/pip -r requirements.txt` in this directory

Then it can be run using `./app.py`


## Getting the animations

Animations are not version controlled, currently are stored on Wee Archie. There is a mirror here:

 - [Wee Archie LED Animations V1.0.0](https://drive.google.com/drive/folders/195ygSV9NNhSlAzoanRW8iLGYSZtQCyJQ?usp=sharing)

## Potential Improvements

 - Store animations in a git compatible way
 - Create a more concise rest API
 - Improve node to node communications - connect servers using pipes, sockets,
   MPI, or similar.
 - Use a proper database for the state of the server, rather than global
   variables.
 - Store history to allow rewinding, pausing, detailed speed control.
 - Use priority queue or similar to set "logging level" of animations, allowing
   for optional animations, mandatory ones, etc.
