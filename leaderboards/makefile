# Creates a Docker image for the leaderboards server

SSH_KEY=~/.ssh/eu-west-1-ec2.pem
SERVER_HOST=ec2-3-249-19-236.eu-west-1.compute.amazonaws.com

.PHONY: image Makefile

image:
	docker build -t pysol-leaderboards:latest .

upload: image
	docker save pysol-leaderboards:latest > pysol-leaderboards.tar
	scp -i $(SSH_KEY) ./pysol-leaderboards.tar ubuntu@$(SERVER_HOST):~/
	rm pysol-leaderboards.tar
	ssh -i $(SSH_KEY) ubuntu@$(SERVER_HOST) "docker load < ~/pysol-leaderboards.tar && rm ~/pysol-leaderboards.tar"

deploy: upload
	ssh -i $(SSH_KEY) ubuntu@$(SERVER_HOST) "docker stop pysol-leaderboards || true"
	ssh -i $(SSH_KEY) ubuntu@$(SERVER_HOST) "docker rm pysol-leaderboards || true"
	ssh -i $(SSH_KEY) ubuntu@$(SERVER_HOST) "docker run --rm --name pysol-leaderboards -itd -p 80:80 -v ~/data:/server/data pysol-leaderboards:latest"
	ssh -i $(SSH_KEY) ubuntu@$(SERVER_HOST) "docker logs pysol-leaderboards"
