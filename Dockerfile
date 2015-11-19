# 
FROM java
COPY tmp/ /lib/
# Runs Oracle NoSQL database in its simplest KVLite configuration
EXPOSE 5000
EXPOSE 5001
CMD ["java", "-jar", "lib/kvstore.jar", "kvlite", "-host", "localhost", "-port", "5000"]
