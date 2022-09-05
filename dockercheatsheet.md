# Docker Cheat sheet: 

To run docker compose file: 
    docker-compose up

To build a dockerfile: 

    docker build -t imagename .

remove all active docker containers: 

    docker rm -f $(docker ps -a -q)


