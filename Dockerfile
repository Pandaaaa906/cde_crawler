FROM python:3.12-bullseye as cde_base

RUN mkdir -p ~/.pip \
    && echo "[global]\nindex-url = https://mirrors.aliyun.com/pypi/simple/" | tee ~/.pip/pip.conf \
    && git config --global http.sslverify false \
    && sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list

RUN apt update && apt -y install libnss3 xvfb gconf-service libasound2 libatk1.0-0 libc6 libcairo2 libcups2 \
libdbus-1-3 libexpat1 libfontconfig1 libgbm1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 \
libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 \
libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 \
libxtst6 ca-certificates fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils wget && \
rm -rf /var/lib/apt/lists/*

VOLUME /ms-playwright
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
COPY ./requirements /tmp/requirements
RUN pip install -r /tmp/requirements
RUN playwright install chromium

FROM cde_base

COPY ./cde_crawler /app/cde_crawler
WORKDIR /app

ENTRYPOINT ["python3", "-m", "cde_crawler.cmdline", "run-scrap-cde"]

