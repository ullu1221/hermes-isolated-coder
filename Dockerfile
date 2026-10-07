FROM node:20-slim
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv git curl ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /workspace
COPY package.json requirements.txt run.sh ./
RUN npm install && python3 -m venv /opt/venv && /opt/venv/bin/pip install -r requirements.txt
ENV PATH="/opt/venv/bin:$PATH"
COPY config/ ./config/
COPY skills/ ./skills/
RUN chmod +x run.sh && git config --global --add safe.directory /workspace
ENTRYPOINT ["./run.sh"]
