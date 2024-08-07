FROM python:3.12.4-alpine
LABEL Maintainer="LRVT"

COPY requirements.txt xingdumper.py /app/.
RUN pip3 install -r /app/requirements.txt

WORKDIR /app
ENTRYPOINT [ "python", "xingdumper.py"]

CMD [ "python", "xingdumper.py", "--help"]
