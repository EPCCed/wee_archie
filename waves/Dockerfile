FROM debian:stable-slim
WORKDIR /opt/workdir
RUN apt-get update && apt-get install -y vim nano git python3-pip libglu1-mesa libgtk-3-dev libnotify-dev && git clone https://github.com/EPCCed/wee_archie.git && pip3 install -r wee_archie/waves/Requirements.txt && pip3 install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/debian-9/wxPython-4.0.4-cp35-cp35m-linux_x86_64.whl wxPython
WORKDIR /opt/workdir/wee_archie/waves
ENV DISPLAY 10.0.75.1:0.0
