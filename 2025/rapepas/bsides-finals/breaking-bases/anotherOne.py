#!/usr/bin/env sage
from sage.all import Matrix, vector, ZZ

def solve_lattice(p, a, b, c, d, m1, m2, m3):
    """
    Resolve o sistema usando LLL + SVP (não CVP).
    """
    print("\n=== A construir a lattice ===")
    
    # 1. Calcular K1 e K2 (CORRIGIDO)
    K1 = ((1 + d) * m1 - m2) % p
    K2 = ((1 + d) * m2 - m3 - (d - c) * m1) % p
    
    print(f"K1 = {K1}")
    print(f"K2 = {K2}")
    
    # 2. Coeficientes das equações
    c_a0 = a % p
    c_a1 = (b - a) % p
    c_a2 = (c - b) % p
    c_a3 = (d - c) % p
    
    c_b1 = a % p
    c_b2 = (b - a) % p
    c_b3 = (c - b) % p
    
    # 3. Construir a matriz da lattice (método SVP, não CVP)
    # Queremos encontrar vetor curto (s0, s1, s2, s3, 0, 0, 1)
    # tal que c_a0*s0 + c_a1*s1 + c_a2*s2 + c_a3*s3 ≡ K1 (mod p)
    #      e     c_b1*s1 + c_b2*s2 + c_b3*s3 ≡ K2 (mod p)
    
    W = 2**66  # Weight para as incógnitas pequenas
    
    M = Matrix(ZZ, [
        [W,  0,  0,  0,  c_a0, 0,    0],
        [0,  W,  0,  0,  c_a1, c_b1, 0],
        [0,  0,  W,  0,  c_a2, c_b2, 0],
        [0,  0,  0,  W,  c_a3, c_b3, 0],
        [0,  0,  0,  0,  p,    0,    0],
        [0,  0,  0,  0,  0,    p,    0],
        [0,  0,  0,  0,  -K1,  -K2,  1]
    ])
    
    print("A executar LLL...")
    M_LLL = M.LLL()
    print("✓ LLL concluído\n")
    
    # 4. Procurar vetor com última coordenada = ±1
    B = 2**64
    for i in range(M_LLL.nrows()):
        v = M_LLL[i]
        
        if abs(v[6]) == 1:  # Última coordenada = ±1
            # Normalizar sinal
            if v[6] == -1:
                v = -v
            
            # Extrair candidatos (dividir por W e arredondar)
            s0_cand = round(ZZ(v[0]) / W)
            s1_cand = round(ZZ(v[1]) / W)
            s2_cand = round(ZZ(v[2]) / W)
            s3_cand = round(ZZ(v[3]) / W)
            
            # Verificar bounds
            if all(0 < abs(x) < B for x in [s0_cand, s1_cand, s2_cand, s3_cand]):
                # Converter para positivos se necessário
                s0 = s0_cand if s0_cand > 0 else s0_cand + p
                s1 = s1_cand if s1_cand > 0 else s1_cand + p
                s2 = s2_cand if s2_cand > 0 else s2_cand + p
                s3 = s3_cand if s3_cand > 0 else s3_cand + p
                
                # Verificar se satisfaz as equações
                check1 = (c_a0*s0 + c_a1*s1 + c_a2*s2 + c_a3*s3) % p
                check2 = (c_b1*s1 + c_b2*s2 + c_b3*s3) % p
                
                if check1 == K1 and check2 == K2:
                    print(f"✓ Solução encontrada no vetor {i}!")
                    return (s0, s1, s2, s3)
                else:
                    print(f"× Vetor {i} tem bounds OK mas não satisfaz equações")
    
    print("✗ Nenhuma solução encontrada na base LLL")
    return None

def main():
    print("=== Breaking Bad (Bases) - Lattice Attack ===\n")
    
    # Dados do desafio
    p = 287876692519385687294901064478745169133
    a = 132538490704636058688740608443237236895
    b = 38377260243245066329208186026249007001
    c = 206172444918008613890240943595900127086
    measurements = [112191803829351766218879789773835272296,
                    146262447593996673654147940903299718988,
                    262643977426427509977095578682468011361]
    m1, m2, m3 = measurements
    
    # Candidatos de 'd' para testar
    d_candidates = {
        "Alice_Igual": 163157290429967258856166843965534378824,
        "Bob_Igual": 56566756732912324004044617489633853617,
        "Alice_Full": 56671514866526957080192048486514900142387895611843634263794115931792346663992 % p,
        "Bob_Full": 22908307150687772680208828841077940795934550099415991184975528191680089001156 % p,
        "XOR": 36155575621823407876114060328053366883522439534275862689595672201918094426364 % p,
    }
    
    for name, d in d_candidates.items():
        print(f"\n{'='*60}")
        print(f"Testando: {name}")
        print(f"d = {d}")
        print('='*60)
        
        solution = solve_lattice(p, a, b, c, d, m1, m2, m3)
        
        if solution:
            s0, s1, s2, s3 = solution
            print(f"\n🎉 SUCESSO com '{name}'!")
            print(f"s0 = {s0}")
            print(f"s1 = {s1}")
            print(f"s2 = {s2}")
            print(f"s3 = {s3}")
            
            # Construir a chave (CORRIGIDO)
            key = 0
            for x in [s0, s1, s2, s3]:
                key <<= 128
                key += x
            key_bytes = int(key).to_bytes(64, "little")
            
            print(f"\nChave (hex): {key_bytes.hex()}")
            print("\n✓ Agora podes decifrar com esta chave!")
            break
    else:
        print("\n✗ Nenhum 'd' funcionou. Verifica os dados ou tenta outras combinações.")

if __name__ == "__main__":
    main()