from scapy.all import *
scapy_cap = rdpcap('capture.pcap')
key = bytes.fromhex('8a490202223d0aa9')
ordered_pkts = []
for packet in scapy_cap:
  if len(packet[Raw]) >= 400:
    data = bytes(packet[Raw])
    # first 16 bytes are the order of the packet
    order = data[:16]
    # they are in big endian
    order_int = int.from_bytes(order, byteorder='big')
    ordered_pkts.append((order_int, packet))
    ordered_pkts.sort()
zip_file = b''
for packet in ordered_pkts[0:]:
  data = bytes(packet[1][Raw])
  payload = data[16:]
  # need to xor the payload with the key 8a490202223d0aa9
  decrypted_payload = b''
  for i in range(len(payload)):
    decrypted_payload += bytes([payload[i] ^ key[i % len(key)]])
  zip_file += decrypted_payload
with open('archive.zip', 'wb') as f:
  f.write(zip_file)
