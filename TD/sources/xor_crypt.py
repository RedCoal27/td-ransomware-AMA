from itertools import cycle


def xor_crypt(data:bytes, key:bytes)->bytes:
    # encrypt and decrypt bytes
    
    # Loop the key (abc become abcabcabcab....)
    infinite_key = cycle(key)
    # create couple from data and key.
    match = zip(data, infinite_key)
    # XOR key and data
    tmp = [a ^ b for a,b in match]
    # return encrypted or decrypted data
    return bytes(tmp)

def xor_file(filename:str, key:bytes)->bytes:
    plain = ""
    # encrypt and decrypt file
    # print("Encrypting file: ", filename)
    # load the file
    with open(filename, "rb") as f:
        plain = f.read()
    # Do the job
    encrypted = xor_crypt(plain, key)
    # write the result on the same file
    with open(filename, "wb") as f:
        f.write(encrypted)