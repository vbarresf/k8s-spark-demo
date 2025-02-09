FROM puckel/docker-airflow:latest
USER 0

# Install Google Cloud SDK

RUN apt-get update && apt-get install -yqq gnupg
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
RUN apt-get install -yqq apt-transport-https ca-certificates

RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
RUN apt-get update &&  apt-get install -yqq google-cloud-sdk
# Install kubectl
RUN apt-get update &&  apt-get install -yqq kubectl

USER airflow

COPY requirements.txt /user/requirements.txt
RUN $(command -v pip) install --user -r /user/requirements.txt


