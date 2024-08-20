import json
import os
import json

private_key = [0, 1]

path = os.path.join(os.path.dirname(__file__), 'key.json')

with open(path) as read_file:
    data = json.load(read_file)
    private_key[0] = data["private_key"][0]
    private_key[1] = data["private_key"][1]


def deserialize_enc_logs(input):
    int_array = []
    temp_str_num = ""
    for char in input:
        if " " != char != ",":
            temp_str_num += char
        elif char == ",":
            int_array.append(int(temp_str_num))
            temp_str_num = ""
    return int_array


def decrypt(input):
    target_enc_data = deserialize_enc_logs(input)

    temp_arr = bytearray()

    for s in target_enc_data:

        to_int = int(s)
        temp = to_int ** private_key[1] % private_key[0]
        if temp > 255:
            continue
        temp_arr.append(temp)

    return temp_arr.decode()
