# =================================================================
# SECOND MYSQL INSTANCE (Port 3307)
# =================================================================

# IMPORTANT: To connect use Allow Public Key Retrieval

docker pull mysql:8.4.5

docker run -d \
  --name mysql-container-2 \
  -e MYSQL_ROOT_PASSWORD=rootpassword456 \
  -e MYSQL_DATABASE=myapp2 \
  -e MYSQL_USER=appuser2 \
  -e MYSQL_PASSWORD=userpassword456 \
  -p 3307:3306 \
  mysql:8.4.5

# =================================================================
# THIRD MYSQL INSTANCE (Port 3308)
# =================================================================

docker run -d \
  --name mysql-container-3 \
  -e MYSQL_ROOT_PASSWORD=rootpassword789 \
  -e MYSQL_DATABASE=myapp3 \
  -e MYSQL_USER=appuser3 \
  -e MYSQL_PASSWORD=userpassword789 \
  -p 3308:3306 \
  mysql:8.4.5