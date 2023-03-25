# Run project
1. ```docker build -t tthack/backend  .```
2. ```docker run --restart=always --network=host tthack/backend``` - if you need to request the localhost (for tests)
3. ```docker run -d -p 80:80 --restart=always tthack/backend``` - prod mode