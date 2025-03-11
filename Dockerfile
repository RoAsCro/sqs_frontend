FROM python:3.10-alpine3.20
WORKDIR /app
ADD ./apiapp/requirements.txt /app/requirements.txt
RUN pip3 install -r ./requirements.txt
COPY ./apiapp /app
EXPOSE 5000
CMD ["gunicorn", "--bind","0.0.0.0:5000", "--timeout", "0", "app:create_app()"]