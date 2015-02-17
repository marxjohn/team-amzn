FROM amazon/aws-eb-python:3.4.2-onbuild-3.5.1
 
RUN apt-get update
RUN apt-get --yes --force-yes install build-essential python3-dev python3-setuptools \
                     python3-numpy python3-scipy libatlas-dev libatlas3gf-base \
                     python-matplotlib
RUN update-alternatives --set libblas.so.3 \
    /usr/lib/atlas-base/atlas/libblas.so.3
RUN update-alternatives --set liblapack.so.3 \
    /usr/lib/atlas-base/atlas/liblapack.so.3
 
# Add and install secondary Python modules
RUN if [ -f aws-post-install/requirements.txt ]; then /var/app/bin/pip install -r aws-post-install/requirements.txt; fi

EXPOSE 8080
