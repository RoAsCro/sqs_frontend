FROM python
WORKDIR /app
COPY ./apiapp /app
EXPOSE 5000
RUN pip3 install -r ./requirements.txt
CMD ["python","./app.py"]