FROM tensorflow/tensorflow
RUN apt update && yes | apt upgrade
RUN mkdir -p /tensorflow/models
RUN apt install -y git python3-pip
RUN pip install --upgrade pip
RUN apt install -y protobuf-compiler python-pil python-lxml
RUN git clone https://github.com/tensorflow/models.git /tensorflow/models
WORKDIR /tensorflow/models/research
RUN protoc object_detection/protos/*.proto --python_out=.

ENV DEBIAN_FRONTEND=noninteractive
RUN apt install -y python3-opencv
RUN pip install requests tf_slim
RUN mkdir -p /app
WORKDIR /app/
COPY app /app/app
ENV PYTHONPATH=/app:/tensorflow/models/research
RUN python3 app/detect_image.py # download model
CMD ["python3","app/main.py"]
