FROM python:3.9-slim
WORKDIR /APP
COPY ./chatbot.py /APP
COPY ./app.py /APP
COPY ./ChatGPT_HKBU.py /APP
COPY ./config.ini /APP
COPY ./requirements.txt /APP
RUN pip install pip update
RUN pip install -r requirements.txt

EXPOSE 10000

CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
