FROM python:3.9-slim
WORKDIR /APP
COPY ./chatbot.py /APP
COPY ./app.py /APP
COPY ./ChatGPT_HKBU.py /APP
COPY ./config.ini /APP
COPY ./requirements.txt /APP
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

CMD python app.py
