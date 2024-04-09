DEADBEEF = 'DEADBEEF'
ENCODER = 'iso-8859-1'

while True:
    file_name_input = input("Enter the name of the file you want to encrypt (including extension - .txt):\n")
    if not file_name_input.endswith('.txt'):
        print("ERROR: The file extension must be '.txt'. Please try again.")
        continue
    try:
        with open(file_name_input, 'r') as file:
            content = file.read()
            if not content:
                print(f"ERROR MESSAGE: The file '{file_name_input}' is empty.")
                continue
    except FileNotFoundError:
        print(f"ERROR: The file '{file_name_input}' was not found. Please try again.")
        continue
    break

while True:
    file_name_output = input("Enter the name for the output file (without extension):\n")
    file_name_output = file_name_output.split('.')[0]  # Remove any existing file extensions
    if len(file_name_output) == 0:
        print("ERROR: Please provide a valid output file name.")
        continue
    break


while True:
    secret_key = input("Enter a 16-character secret phrase:\n")
    if len(secret_key) != 16:
        print("ERROR: The secret phrase must be exactly 16 characters long.")
        continue
    else:
        break


def generate_key():
    enc_secret_key = secret_key.encode(ENCODER)
    left = enc_secret_key[:8]
    right = enc_secret_key[8:16]

    xor_left = bytes(x ^ y for x, y in zip(left, DEADBEEF.encode(ENCODER)))
    xor_right = bytes(x ^ y for x, y in zip(right, DEADBEEF.encode(ENCODER)))

    complete_key = xor_left + xor_right
    return (
        complete_key[:4],
        complete_key[4:8],
        complete_key[8:12],
        complete_key[12:16]
    )


def xor_deadbeef(data):
    utf_db = DEADBEEF.encode(ENCODER)
    result = bytes(x ^ y for x, y in zip(data, utf_db))
    return result


def plain_text_process(data):
    bytes_text = data.encode(ENCODER)

    chunk_num = len(bytes_text) // 8
    chunks = [bytes_text[i * 8:8 * (i + 1)] for i in range(chunk_num)]
    if len(bytes_text) % 8 != 0:
        chunks.append(bytes_text[chunk_num * 8:].ljust(8, b'\x00'))

    return chunks


def nibble(data):
    order = [3, 7, 1, 5, 2, 4, 0, 6]

    binary_data = ''.join(format(byte, '08b') for byte in data)
    chunks = [binary_data[i * 4:4 * (i + 1)] for i in range(len(binary_data) // 4)]

    new_chunks = [chunks[i] for i in order]
    final_chunks = ''.join(new_chunks)
    byte_chunks = [final_chunks[i:i + 8] for i in range(0, len(final_chunks), 8)]
    decimal_val = [int(chunk, 2) for chunk in byte_chunks]
    return bytes(decimal_val)


def encrypt(data):
    key = generate_key()

    ciphertext = b''
    chunks = plain_text_process(data)
    for chunk in chunks:
        data_a = chunk[:4]
        data_b = chunk[4:8]

        data_a = bytes(x ^ y for x, y in zip(data_a, key[0]))
        data_b = bytes(x ^ y for x, y in zip(data_b, key[1]))

        for _ in range(4):
            new_data_b = nibble(data_b)
            data_a, data_b = new_data_b, data_a

        data_a = bytes(x ^ y for x, y in zip(data_a, key[2]))
        data_b = bytes(x ^ y for x, y in zip(data_b, key[3]))

        ciphertext += data_a + data_b

    return ciphertext.decode(ENCODER)


with open(file_name_input, 'r') as file_input:
    file_content = file_input.read()

output_file_name = file_name_output + '.ctx'

with open(output_file_name, 'w', encoding=ENCODER) as file_output:
    file_output.write(encrypt(file_content))

print(f"The file '{output_file_name}' has been successfully encrypted.")
