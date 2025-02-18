FROM python
WORKDIR /app
COPY ./apiapp /app
EXPOSE 5000
RUN pip3 install -r ./requirements.txt
CMD ["gunicorn", "--bind","0.0.0.0:5000", "app:create_app()"]