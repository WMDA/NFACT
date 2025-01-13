FROM python:3.11-slim

WORKDIR /app
COPY ./ /app/NFACT
RUN pip install /app/NFACT
ENV PYTHONPATH=/app/NFACT
ENTRYPOINT ["python", "/app/NFACT/NFACT/dual_reg/cluster/regression_scripts/cluster_script.py"]