import pefile

# Load the decrypted DLL
pe = pefile.PE('decrypted_object.bin')

# The RVA of the key based on the assembly (0x18001b440 - 0x180000000 base)
rva = 0x1b440
key_length = 32

# Dump the raw bytes at that RVA
key_bytes = pe.get_data(rva, key_length)

print(key_bytes.hex())