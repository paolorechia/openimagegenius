FROM python:3.9.9-bullseye

WORKDIR /src

RUN apt-get update && \
    apt-get install -y \
    libgl1 libglib2.0-0 \
    g++ \
    make \
    cmake \
    unzip \
    libcurl4-openssl-dev

COPY requirements.txt /src/

COPY models/clip /src/models/clip
 
RUN pip3 install -r requirements.txt --target /src/
COPY handler.py stable_diffusion_engine.py /src/

ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]
CMD [ "handler.handler" ]