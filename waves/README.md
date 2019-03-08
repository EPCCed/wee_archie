## Docker Instructions

### Prerequisites:
 - Docker for your computer.
 - An X server.

### X server set-up:
#### Windows
[XMing](http://www.straightrunning.com/XmingNotes/) is the recommended X server provider. Launch it using XLaunch so that you can select `No Access Control`, which is necessary to allow the container to connect to the host side X server.
#### Mac OS
[XQuartz](https://www.xquartz.org/) is the recommended X server provider. Make sure to select `Allow connections from network clients` in the XQuartz options. XQuartz will then need to be restarted.
#### Linux
...should just work, assuming you're running a graphical OS. If not you will need to install an X server. May require an additional argument to `docker run`, requires testing.

### Docker image set-up:
 - Open a terminal with Docker in its path.
 - `docker pull otbrown/wave-demo:1.3`
 - Run `docker image list` to check the image has pulled successfully.

**Note**: Once the docker image is successfully pulled, an internet connection is no longer necessary.

### Running the demo:
#### Windows
 - Launch the XMing, ensuring `No Access Control` is selected.
 - `docker run --rm -it otbrown/wave-demo:1.3`
 - `python3 Start.py`

**Note**: Nothing from this instance of the container will be preserved on `exit`. Use `docker cp` to copy out any files you wish to retain (such as the logs).
