FROM python:3

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# for custom_actions.py (if any)
ENV PYTHONPATH /src

CMD [ "python", "./file_server.py" ]
# TODO: run with gunicorn
