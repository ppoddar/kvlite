# -------------------------------------------------------------
# Builds Oracle NOSQL database Image
# -------------------------------------------------------------
# Main Steps:
#   -- Downloads Community Edition from OTN site
#   -- Unpacks the libraries
#   -- runs the simplest configuration with single partition on local host
# -------------------------------------------------------------
FROM java

ENV KV_VERSION 3.4.7 
ENV DOWNLOAD_ROOT http://download.oracle.com/otn-pub/otn_software/nosql-database
ENV DOWNLOAD_FILE kv-ce-$KV_VERSION.zip
ENV DOWNLOAD_LINK  $DOWNLOAD_ROOT/$DOWNLOAD_FILE
ENV UNZIPPED_LIB  kv-$KV_VERSION/lib

RUN wget  $DOWNLOAD_LINK
RUN unzip $DOWNLOAD_FILE $UNZIPPED_LIB/* 


EXPOSE 5000
EXPOSE 5001

CMD ["java", "-jar", "kv-3.4.7/lib/kvstore.jar", "kvlite", "-host", "localhost", "-port", "5000"]
