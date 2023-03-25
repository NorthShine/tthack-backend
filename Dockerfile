FROM python:3.11

WORKDIR /usr/src/app

COPY . .

RUN apt-get update && apt-get -y install libgl1-mesa-glx
RUN pip install -r requirements.txt

EXPOSE 5001

CMD ["python", "app.py"]