FROM python:3-alpine

COPY requirements.txt /.
COPY main.py /.

RUN set -x && pip install --no-cache-dir -r requirements.txt

CMD ["python", "/main.py"]
