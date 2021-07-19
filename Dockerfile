FROM proycon/lamachine:core
MAINTAINER Maarten van Gompel <proycon@anaproy.nl>
MAINTAINER Jaap Blom <jblom@beeldengeluid.nl>
LABEL description="A LaMachine installation with Kaldi NL and Oral History (CLST)"
#RUN lamachine-config lm_base_url https://your.domain.here
#RUN lamachine-config force_https yes
#RUN lamachine-config private true
#RUN lamachine-config maintainer_name "Your name here"
#RUN lamachine-config maintainer_mail "your@mail.here"
RUN lamachine-add kaldi_nl
RUN lamachine-add oralhistory
RUN lamachine-update

#install DANE worker dependencies
RUN sudo apt-get update

# intall ffmpeg, so the input video files will be transcoded to mp3
RUN sudo apt-get install -y \
    ffmpeg

# add the Python code & install the required libs
COPY . /src
COPY requirements.txt /src/
RUN pip3 install -r /src/requirements.txt

RUN sudo mkdir /src/log && sudo chmod -R 777 /src/log
RUN sudo mkdir /src/pid-cache && sudo chmod -R 777 /src/pid-cache

#make sure to set the KALDI_ROOT or kaldi_NL won't be able to locate it
ENV KALDI_ROOT=/usr/local/opt/kaldi

WORKDIR /src

#start the dane worker
#CMD ["python3","-u","/src/worker.py"]
CMD ["python3","-u","server.py"]