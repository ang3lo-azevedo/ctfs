def solve():
    # A matriz hardcoded v5 extraída do decompiler
    v5_signed = [
        37, 46, 34, -41, -63, 114, -41, 110,
        -77, 42, -93, -15, -8, -22, -16, -80,
        87, -43, -24, -30, 11, 127, 8, 77,
        -49, -40, 0, -24, -5, -115, 107, 33,
        -69, -115, -8, 124, -1, -48, -22, -78,
        -6, -115, -93, -14, 119, -109, -93, -49,
        105, -117, -79, 116, 10, -70, -63, -39,
        -110, -62, -62, -115, 79, 45, -82, 10
    ]
    
    # Converter os valores com sinal de 8-bits para sem sinal (0-255)
    v5 = [x & 0xFF for x in v5_signed]
    
    # O resultado hexadecimal que a aplicação usa (v6)
    v6_hex = "25d1278bc47a3188b3d55cf09094fd27572a87789b8892f8cf27ee39e0b6b056bb722348937ed40ffa724c4ce6c719966964405996643eb7929d253c521810ff"
    v6 = bytes.fromhex(v6_hex)
    
    flag = bytearray(64)
    
    # Processar bloco a bloco (8 blocos de 8 bytes)
    for block in range(8):
        offset = block * 8
        
        # 1. Aplicar XOR do hash (v6) com a chave hardcoded (v5)
        diff = bytearray(8)
        for i in range(8):
            diff[i] = v6[offset + i] ^ v5[offset + i]
        
        # 2. Reverter a transposição da matriz de bits 8x8
        for col in range(8):
            char_val = 0
            for row in range(8):
                # Extrair o bit necessário da matriz 'diff'
                bit = (diff[7 - row] >> (7 - col)) & 1
                # Colocá-lo na posição correspondente para formar o caracter final
                char_val |= (bit << row)
            flag[offset + col] = char_val
            
    print(f"[*] A Flag recuperada é: {flag.decode('utf-8')}")

if __name__ == '__main__':
    solve()