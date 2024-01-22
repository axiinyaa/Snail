FROM python:3.11 
WORKDIR /among
COPY requirements.txt /among/
RUN pip install -r requirements.txt
COPY . /among
CMD python main.py