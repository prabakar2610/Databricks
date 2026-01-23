# prabakar2610/rbase14:v2
FROM databricksruntime/standard:9.x

# Suppress interactive configuration prompts
ENV DEBIAN_FRONTEND=noninteractive

# update indices
RUN apt-get update -qq
# install two helper packages we need
RUN apt-get install --no-install-recommends software-properties-common dirmngr -y
# add the signing key (by Michael Rutter) for these repos
# To verify key, run gpg --show-keys /etc/apt/trusted.gpg.d/cran_ubuntu_key.asc 
# Fingerprint: 298A3A825C0D65DFD57CBB651716619E084DAB9
RUN wget -qO- https://cloud.r-project.org/bin/linux/ubuntu/marutter_pubkey.asc | sudo tee -a /etc/apt/trusted.gpg.d/cran_ubuntu_key.asc
# add the R 4.0 repo from CRAN -- adjust 'focal' to 'groovy' or 'bionic' as needed
RUN add-apt-repository "deb https://cloud.r-project.org/bin/linux/ubuntu $(lsb_release -cs)-cran40/"

RUN apt-get install --no-install-recommends r-base -y 

RUN add-apt-repository ppa:c2d4u.team/c2d4u4.0+
#RUN apt-get install --no-install-recommends r-cran-rstan -y 
RUN apt install --no-install-recommends r-cran-tidyverse -y

# hwriterPlus is used by Databricks to display output in notebook cells
# Rserve allows Spark to communicate with a local R process to run R code
RUN R -e "install.packages(c('hwriterPlus'), repos='https://mran.revolutionanalytics.com/snapshot/2017-02-26')" \
 && R -e "install.packages(c('htmltools'), repos='https://cran.microsoft.com/')" \
 && R -e "install.packages('Rserve', repos='http://rforge.net/')"

 # Databricks configuration for RStudio sessions.
COPY Rprofile.site /usr/lib/R/etc/Rprofile.site

# Rstudio installation v1
# RUN apt-get update \
#  # Installation of rstudio in databricks needs /usr/bin/python.
#  && apt-get install -y python \
#  # Install gdebi-core.
#  && apt-get install -y gdebi-core \
#  # Download rstudio 1.2 package for ubuntu 18.04 and install it.
#  && apt-get install -y wget \
#  && wget https://download2.rstudio.org/server/bionic/amd64/rstudio-server-2021.09.0-351-amd64.deb -O rstudio-server.deb \
#  && gdebi -n rstudio-server.deb \
#  && rm rstudio-server.deb

# Rstudio installation v2
RUN apt-get update \
 # Installation of rstudio in databricks needs /usr/bin/python.
 && apt-get install -y python \
 # Install gdebi-core.
 && apt-get install -y gdebi-core \
 # Download rstudio 1.2 package for ubuntu 18.04 and install it.
 && apt-get install -y wget \
 && wget https://download2.rstudio.org/server/bionic/amd64/rstudio-server-1.2.5042-amd64.deb -O rstudio-server.deb \
 && gdebi -n rstudio-server.deb \
 && rm rstudio-server.deb

RUN apt-get clean \
&& rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*