FROM python:3.9

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /requirements.txt
RUN pip install -r requirements.txt

COPY games/. /games/.
COPY templates/. /templates/.
COPY bgQA.py /bgQA.py
COPY CreateVectorDb.py /CreateVectorDb.py
COPY main.py /main.py

EXPOSE 5000

CMD [ "gunicorn", "--timeout=6000", "--bind=0.0.0.0:5000", "--workers=4", "main:app" ]