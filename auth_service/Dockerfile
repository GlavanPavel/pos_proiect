FROM python:3.11-slim

WORKDIR /app

# pentru bcrypt
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY auth_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY auth_service/ auth_service/

RUN mkdir -p auth_service/generated auth_service/proto && \
    touch auth_service/__init__.py auth_service/generated/__init__.py

COPY auth_service/proto/auth.proto auth_service/proto/

RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. auth_service/proto/auth.proto && \
    mv auth_service/proto/auth_pb2.py auth_service/generated/ && \
    mv auth_service/proto/auth_pb2_grpc.py auth_service/generated/ && \
    # corectie import grpc
    sed -i 's/from auth_service.proto import auth_pb2/from auth_service.generated import auth_pb2/' auth_service/generated/auth_pb2_grpc.py

ENV PYTHONPATH=/app
EXPOSE 50051

CMD ["python", "-m", "auth_service.auth_server"]