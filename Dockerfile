FROM python:3.10.11

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

COPY ./packages.txt /code/packages.txt

RUN apt-get update && apt-get install -y libsm6 libxrender1 libfontconfig1 libice6 ffmpeg libxext6 libgl1 libgl1-mesa-glx

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . .

RUN chmod -R 777 .

EXPOSE 7860

CMD ["python", "app.py", "--host", "0.0.0.0", "--port", "7860"]