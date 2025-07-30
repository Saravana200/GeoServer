FROM python:3.10-slim

COPY requirements.txt .

RUN pip install -r requirements.txt && pip cache purge

COPY . .

EXPOSE 8036

ENTRYPOINT ["./entrypoint.sh"]