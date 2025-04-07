FROM python:3.9-slim
WORKDIR /APP
COPY ./chatbot.py /APP
COPY ./app.py /APP
COPY ./ChatGPT_HKBU.py /APP
COPY ./config.ini /APP
COPY ./requirements.txt /APP
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

ENV REDIS_HOST=redis://red-cvplh6s9c44c73c540k0:6379
ENV REDIS_PORT=6379

CMD python app.py
