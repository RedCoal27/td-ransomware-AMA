mkdir -p token_data
docker run -it --rm --name ransomware \
    --net=ransomware-network \
    -v "$PWD"/sources:/root/ransomware:ro \
    -v "$PWD"/token_data:/root/token:rw \
    -v "$PWD"/some_data:/root/some_data \
    ransomware \
    python /root/ransomware/dropper.py $1\