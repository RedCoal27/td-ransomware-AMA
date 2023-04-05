import base64

#input a token in hexa
input_key = input("Enter the token: ")



path = "cnc_data/" + input_key + "/key.bin"
#read the key
with open(path, "rb") as key_file:
    key = key_file.read()

#print the key
print("The key is: " + base64.b64encode(key).decode("utf-8"))