FROM python:3.6
ENV DOCKER_CONTAINER=1

COPY ./cde_crawler /cde_crawler
COPY ./requirements /cde_crawler
WORKDIR /cde_crawler

COPY ./local-chromium /pyppeteer_home/local-chromium
ENV PYPPETEER_HOME=/pyppeteer_home

RUN mkdir ~/.pip
RUN echo "[global]\nindex-url = https://pypi.tuna.tsinghua.edu.cn/simple" | tee ~/.pip/pip.conf
RUN pip install -r requirements

RUN python3 models.py

CMD python3 scrap_cde.py