FROM python:3.11

ENV APP_HOME /app
ENV HTTP_PORT=3000
ENV SOCKET_PORT=5000
ENV DATA_FILE=/data/data.json

WORKDIR $APP_HOME

COPY . .

RUN pip install pipenv
RUN pipenv install flask

CMD ["python", "main.py"]