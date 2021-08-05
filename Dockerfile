FROM proycon/lamachine:core
MAINTAINER Maarten van Gompel <proycon@anaproy.nl>
MAINTAINER Jaap Blom <jblom@beeldengeluid.nl>
LABEL description="A LaMachine installation with Kaldi NL and Oral History (CLST)"
RUN lamachine-add kaldi_nl
RUN lamachine-add oralhistory
RUN lamachine-update

#switch to root user and add the KALDI_ROOT to that user env as well
USER root

# intall ffmpeg, so the input video files will be transcoded to mp3
RUN apt-get update
RUN apt-get install -y \
    ffmpeg

# add the Python code & install the required libs
COPY . /src
COPY requirements.txt /src/
RUN pip3 install -r /src/requirements.txt

RUN mkdir /src/log && chmod -R 777 /src/log
RUN mkdir /src/pid-cache && chmod -R 777 /src/pid-cache

#make sure to set the KALDI_ROOT or kaldi_NL won't be able to locate it
ENV KALDI_ROOT=/usr/local/opt/kaldi

#make sure the DANE fs mount point exists
RUN mkdir /mnt/dane-fs && chmod -R 777 /mnt/dane-fs

WORKDIR /src

#start the Kaldi API
CMD ["python3","-u","server.py"]