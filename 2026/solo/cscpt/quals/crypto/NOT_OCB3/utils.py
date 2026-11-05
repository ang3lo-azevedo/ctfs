import hmac
from Crypto.Cipher import AES

BLOCK_SIZE = 16
MASK_128 = (1 << 128) - 1

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def ntz(x):
    return (x & -x).bit_length() - 1

def pad_10star(partial):
    if len(partial) >= BLOCK_SIZE:
        raise ValueError("pad expects a partial block")
    return partial + b"\x80" + b"\x00" * (BLOCK_SIZE - len(partial) - 1)

def double_block(block):
    x = int.from_bytes(block, "big")
    carry = x >> 127
    x = (x << 1) & MASK_128
    if carry:
        x ^= 0x87
    return x.to_bytes(BLOCK_SIZE, "big")

class NotOCB3:
    def __init__(self, key):
        self.tag_len = 16
        self.ecb = AES.new(key, AES.MODE_ECB)
        self.L_star = self._aes_encrypt(b"\x00" * BLOCK_SIZE)
        self.L_dollar = double_block(self.L_star)
        self.L = [double_block(self.L_dollar)]

    def _aes_encrypt(self, block):
        return self.ecb.encrypt(block)

    def _aes_decrypt(self, block):
        return self.ecb.decrypt(block)

    def _get_L(self, i):
        while i >= len(self.L):
            self.L.append(double_block(self.L[-1]))
        return self.L[i]

    def _offset_0(self, nonce):
        if not (1 <= len(nonce) <= 15):
            raise ValueError("nonce must be between 1 and 15 bytes")

        nonce_block = bytearray(16)
        nonce_block[0] = ((self.tag_len * 8) % 128) << 1
        nonce_block[15 - len(nonce)] |= 1
        nonce_block[16 - len(nonce):] = nonce

        bottom = nonce_block[15] & 0x3F
        nonce_block[15] &= 0xC0

        ktop = self._aes_encrypt(bytes(nonce_block))
        stretch = ktop + xor_bytes(ktop[:8], ktop[1:9])

        stretch_int = int.from_bytes(stretch, "big")
        offset_int = (stretch_int >> (64 - bottom)) & MASK_128
        return offset_int.to_bytes(16, "big")

    def _hash_aad(self, aad):
        offset = b"\x00" * BLOCK_SIZE
        total = b"\x00" * BLOCK_SIZE

        full_blocks = len(aad) // BLOCK_SIZE
        for i in range(1, full_blocks + 1):
            block = aad[(i - 1) * BLOCK_SIZE:i * BLOCK_SIZE]
            offset = xor_bytes(offset, self._get_L(ntz(i)))
            total = xor_bytes(total, self._aes_encrypt(xor_bytes(block, offset)))

        tail = aad[full_blocks * BLOCK_SIZE:]
        if tail:
            offset = xor_bytes(offset, self.L_star)
            total = xor_bytes(
                total,
                self._aes_encrypt(xor_bytes(pad_10star(tail), offset)),
            )

        return total

    def _tag_block(self, checksum, offset_0, has_tail):
        tag_offset = offset_0
        if has_tail:
            tag_offset = xor_bytes(tag_offset, self.L_star)

        tag_input = xor_bytes(checksum, tag_offset)
        tag_input = xor_bytes(tag_input, self.L_dollar)
        return self._aes_encrypt(tag_input)

    def encrypt(self, nonce, plaintext, aad=b""):
        offset_0 = self._offset_0(nonce)
        offset = offset_0
        checksum = b"\x00" * BLOCK_SIZE
        ciphertext = bytearray()

        full_blocks = len(plaintext) // BLOCK_SIZE
        for i in range(1, full_blocks + 1):
            block = plaintext[(i - 1) * BLOCK_SIZE:i * BLOCK_SIZE]
            offset = xor_bytes(offset, self._get_L(ntz(i)))
            checksum = xor_bytes(checksum, block)

            cblock = xor_bytes(self._aes_encrypt(xor_bytes(block, offset)), offset)
            ciphertext.extend(cblock)

        tail = plaintext[full_blocks * BLOCK_SIZE:]
        if tail:
            offset_star = xor_bytes(offset, self.L_star)
            pad = self._aes_encrypt(offset_star)
            ciphertext.extend(x ^ y for x, y in zip(tail, pad))
            checksum = xor_bytes(checksum, pad_10star(tail))

        tag_block = self._tag_block(checksum, offset_0, bool(tail))
        tag = xor_bytes(tag_block, self._hash_aad(aad))[:self.tag_len]
        return bytes(ciphertext), tag

    def decrypt(self, nonce, ciphertext, tag, aad=b""):
        if len(tag) != self.tag_len:
            raise ValueError("incorrect tag length")

        offset_0 = self._offset_0(nonce)
        offset = offset_0
        checksum = b"\x00" * BLOCK_SIZE
        plaintext = bytearray()

        full_blocks = len(ciphertext) // BLOCK_SIZE
        for i in range(1, full_blocks + 1):
            block = ciphertext[(i - 1) * BLOCK_SIZE:i * BLOCK_SIZE]
            offset = xor_bytes(offset, self._get_L(ntz(i)))

            pblock = xor_bytes(self._aes_decrypt(xor_bytes(block, offset)), offset)
            plaintext.extend(pblock)
            checksum = xor_bytes(checksum, pblock)

        tail = ciphertext[full_blocks * BLOCK_SIZE:]
        if tail:
            offset_star = xor_bytes(offset, self.L_star)
            pad = self._aes_encrypt(offset_star)
            ptail = bytes(x ^ y for x, y in zip(tail, pad))
            plaintext.extend(ptail)
            checksum = xor_bytes(checksum, pad_10star(ptail))

        expected_tag = xor_bytes(
            self._tag_block(checksum, offset_0, bool(tail)),
            self._hash_aad(aad),
        )[:self.tag_len]

        if not hmac.compare_digest(expected_tag, tag):
            raise ValueError("authentication failed")

        return bytes(plaintext)