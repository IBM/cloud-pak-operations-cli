FROM python:3.8
COPY dist/*.whl /root
RUN pip install /root/*.whl
RUN useradd --create-home --gid 0 --no-log-init cpo
# https://docs.openshift.com/container-platform/latest/openshift_images/create-images.html#use-uid_create-images
RUN chmod g=u /home/cpo
ENV HOME /home/cpo
WORKDIR /home/cpo
USER cpo
