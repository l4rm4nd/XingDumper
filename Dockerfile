FROM python:3.9-alpine
LABEL Maintainer="LRVT"

COPY . /app
RUN pip3 install -r /app/requirements.txt

WORKDIR /app
ENTRYPOINT [ "python", "xingdumper.py"]

CMD [ "python", "xingdumper.py", "--help"]
