docker pull mysql:5.7

# Run MySQL container with basic configuration
docker run -d \
  --name mysql-container \
  -e MYSQL_ROOT_PASSWORD=rootpassword123 \
  -e MYSQL_DATABASE=myapp \
  -e MYSQL_USER=appuser \
  -e MYSQL_PASSWORD=userpassword123 \
  -p 3306:3306 \
  mysql:5.7