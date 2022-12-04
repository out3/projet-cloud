FROM ubuntu
RUN apt-get update && apt install -y curl && curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN apt-get install unzip
RUN unzip awscliv2.zip
RUN ./aws/install

