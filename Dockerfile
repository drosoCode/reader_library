FROM python:3.8-slim

WORKDIR /app
ADD . .
RUN pip3 install -r requirements.txt && chmod +x main.py

CMD "/app/main.py"
