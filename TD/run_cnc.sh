docker run -it --rm --name cnc \
    --net=ransomware-network \
    -v "$PWD"/sources:/root/ransomware:ro \
    -v "$PWD"/cnc_data:/root/CNC\
    -v "$PWD"/dist:/root/dist\
    ransomware \
    python /root/ransomware/cnc.py