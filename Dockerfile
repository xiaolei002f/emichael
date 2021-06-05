FROM ubuntu:trusty

MAINTAINER https://github.com/emichael/SlackLaTeXBot


# Install main dependencies first
RUN apt-get update && \
    apt-get install -y \
      python-pip \
      texlive \
      texlive-extra-utils \
      ImageMagick


# Verify and add Tini
ENV TINI_VERSION v0.14.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini.asc /tini.asc
RUN gpg --keyserver ha.pool.sks-keyservers.net --recv-keys \
      595E85A6B1B4779EA4DAAEC70B588DFF0527A9B7 && \
    gpg --verify /tini.asc
RUN chmod +x /tini
ENTRYPOINT ["/tini", "--"]


# Install app
COPY LatexServer.py error.png requirements.txt /
RUN pip install -r requirements.txt
RUN mkdir -p images


# Don't run as root
RUN chmod ugo+rx LatexServer.py && \
    chmod ugo+r error.png requirements.txt && \
    chmod -R ugo+rwx images/
USER nobody


# Setup app
EXPOSE 8642/tcp
ENTRYPOINT ["/tini", "--", "python", "/LatexServer.py"]
