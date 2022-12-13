FROM python:3.8
 
WORKDIR /app
COPY . .
RUN ls ./app
RUN chmod -R 777 ./app/app.py
RUN pip install -r requirements.txt
 
ENTRYPOINT ["python"]
CMD ["app/app.py"]
