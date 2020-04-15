FROM amazonlinux:latest

ARG BUILD_TAG

RUN curl -sL https://rpm.nodesource.com/setup_13.x | bash - \
  && yum -y update \
  && yum -y install nodejs python3 \
  && npm -y install -g aws-cdk@1.32.2 \
  && yum clean all \
  && rm -rf /var/cache/yum

WORKDIR /cdk

COPY . .

RUN python3 -m venv .env \
  && source .env/bin/activate \
  && pip install -r requirements.txt \
  && rm -f version.txt && echo "${BUILD_TAG}" > version.txt \
  && mv /cdk/files/cdk-entrypoint.sh /cdk/ \
  && chmod +x /cdk/cdk-entrypoint.sh

ENTRYPOINT ["/cdk/cdk-entrypoint.sh"]
