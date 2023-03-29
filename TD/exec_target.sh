docker run -it --rm --name ransomware \
    --net=ransomware-network \
    -v "$PWD"/sources:/root/ransomware:ro \
    -v "$PWD"/dist:/root/bin:ro \
    -v "$PWD"/token_data:/root/token \
    -v "$PWD"/some_data:/root/some_data \
    ransomware \
    /bin/bash