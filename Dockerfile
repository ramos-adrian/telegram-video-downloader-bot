FROM amazon/aws-lambda-python:3.8
LABEL authors="ChasisTorcido"

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src

CMD ["src/bot.handler"]
