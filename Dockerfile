# -------------------------------------------------------------
# Builds Oracle NOSQL database Image
# -------------------------------------------------------------
# Main Steps:
#   -- Downloads Community Edition from OTN site
#   -- Unpacks the libraries
#   -- runs the simplest configuration with single partition on local host
# -------------------------------------------------------------
FROM java

ENV DOWNLOAD_ROOT http://download.oracle.com/otn-pub/otn_software/nosql-database
# ENV KV_VESRION 3.4.7 -- variable substitution in ENV varaiables is not supported
#                                     -- Otherwise thhis version variable should be used
ENV DOWNLOAD_LINK=$DOWNLOAD_ROOT/kv-ce-3.4.7.zip


RUN wget -v $DOWNLOAD_LINK
RUN unzip kv-ce-3.4.7.zip


EXPOSE 5000
EXPOSE 5001


CMD ["java", "-jar", "kv-3.4.7/lib/kvstore.jar", "kvlite", "-host", "localhost", "-port", "5000"]
