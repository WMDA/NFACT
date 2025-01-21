FROM python:3.11-slim

WORKDIR /app
COPY ./ /app/NFACT
RUN pip install /app/NFACT
RUN pip install --upgrade joblib loky
ENV PYTHONPATH=/app/NFACT
ENTRYPOINT ["python", "/app/NFACT/NFACT/dual_reg/cluster/regression_scripts/cluster_script.py"]