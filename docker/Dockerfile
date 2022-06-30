# Use miniconda image base from Dockerhub
FROM continuumio/miniconda3

# Metadata
LABEL container.base.image = "miniconda3:python3.9"
# # Use Python image base from Dockerhub
#FROM python:3.7
# LABEL container.base.image = "python:3.7"
LABEL software.name = "sars_cov2_ncbi"

# Install system packages and AWS CLI
RUN apt-get -y update && \
    apt-get -y install python3-pip
RUN pip install awscli boto3
RUN conda install -c anaconda pandas
RUN conda install -c anaconda numpy
RUN conda install -c bioconda sra-tools
WORKDIR /

# INSTALL SRA toolkit
# RUN mkdir /sratoolkit.3.0.0-centos_linux64
# COPY sratoolkit.3.0.0-centos_linux64/ /sratoolkit.3.0.0-centos_linux64/

# install NCBI edirect for accessing NBCI metadata
# RUN sh -c "$(curl -fsSL ftp://ftp.ncbi.nlm.nih.gov/entrez/entrezdirect/install-edirect.sh)"
RUN sh -c "$(wget -q ftp://ftp.ncbi.nlm.nih.gov/entrez/entrezdirect/install-edirect.sh -O -)"

# copy relevant scripts to root dir
RUN mkdir -p global_utils/src
COPY src/run_main.py /
COPY src/run_program.py /
COPY src/global_utils/src/module_utils.py /global_utils/src/
COPY src/global_utils/src/file_utils.py /global_utils/src/
COPY src/global_utils/src/global_keys.py /global_utils/src/
COPY src/global_utils/src/aws_s3_utils.py /global_utils/src/
ENV PATH="/usr/local/bin/:/sratoolkit.3.0.0-centos_linux64/bin:$HOME/edirect:$PATH"

ENTRYPOINT ["python","/run_main.py"] 
