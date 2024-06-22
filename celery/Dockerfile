FROM python:3.8-slim

WORKDIR /app


COPY . .

RUN chmod +x /app/start.sh

RUN pip install -r requirements.txt

CMD ["./start.sh"]
