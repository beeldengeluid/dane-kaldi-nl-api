# TODO add container to CLARIAH image registry
FROM proycon/kaldi_nl:latest
MAINTAINER Jaap Blom <jblom@beeldengeluid.nl>

# switch to root user, to be able to write to the k8s mount, which is root user by default
USER root

# intall ffmpeg, so the input video files will be transcoded to mp3
RUN apt-get update
RUN apt-get install -y \
    ffmpeg

# put all python installation in a separate layer for speed
RUN apt-get install -y \
    python3 \
    python3-pip

# add the Python code & install the required libs
COPY . /src

# create log and cache dirs
RUN mkdir /src/log && chmod -R 777 /src/log
RUN mkdir /src/pid-cache && chmod -R 777 /src/pid-cache

# make sure the DANE fs mount point exists (Note: not needed if lean-kaldi MODELPATH=/mnt/dane-fs/models)
RUN mkdir /mnt/dane-fs && chmod -R 777 /mnt/dane-fs
RUN mkdir /mnt/dane-fs/models && chmod -R 777 /mnt/dane-fs/models

COPY Pipfile Pipfile.lock /src/

WORKDIR /src

RUN pip install pipenv
RUN pipenv sync --system

WORKDIR /src

# start the Kaldi API
ENTRYPOINT ["python", "/src/server.py"]