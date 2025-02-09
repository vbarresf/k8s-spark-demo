FROM airflow-python

USER 0
RUN echo "root:root" | chpasswd
USER airflow
COPY dags /usr/local/airflow/dags
