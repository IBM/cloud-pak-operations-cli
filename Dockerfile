FROM python:3.8
COPY dist/*.whl /root
RUN pip install /root/*.whl
RUN useradd --create-home --gid 0 --no-log-init dg
# https://docs.openshift.com/container-platform/latest/openshift_images/create-images.html#use-uid_create-images
RUN chmod g=u /home/dg
ENV HOME /home/dg
WORKDIR /home/dg
USER dg
