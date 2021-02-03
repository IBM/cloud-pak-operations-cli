FROM python:3.9 AS builder
COPY . /workspace
WORKDIR /workspace
RUN python setup.py sdist

FROM python:3.9-slim
COPY --from=builder /workspace/dist/dg-0.1.0.tar.gz /root/
RUN pip3 install /root/dg-0.1.0.tar.gz
