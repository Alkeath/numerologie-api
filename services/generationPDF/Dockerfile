FROM python:3.10

# 🧱 Install dependencies
RUN apt-get update && apt-get install -y wget ca-certificates fonts-liberation libappindicator3-1 libasound2 \
    libatk-bridge2.0-0 libatk1.0-0 libcups2 libdbus-1-3 libgdk-pixbuf2.0-0 libnspr4 libnss3 \
    libxcomposite1 libxdamage1 libxrandr2 xdg-utils libu2f-udev libvulkan1 \
    --no-install-recommends

# Puppeteer dependencies
RUN apt-get install -y chromium

# 👨‍💻 Workdir
WORKDIR /app

COPY . .

# Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
