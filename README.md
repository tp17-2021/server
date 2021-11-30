# Server

Voting server public API implemented in FastAPI used to accept incoming votes from gateway, import data before voting a provide realtime statistics and evaluation after the end of voting.


## How to run it
Development run without docker, run it from the server directory. Flag --reload makes sure the uvicorn server reloads on any file change.

```
uvicorn src.server.app:app --host localhost --port 80 --reload
```

Clone the repo and navigate inside it. Build the image:

```bash
docker build -t server-image .
```

Run the container:

```bash
docker run -d --name server -p 8222:80 server-image
```

Navigate to ```localhost:8222/docs``` and you should see FastAPI docs for the service.

---

## API description

TODO