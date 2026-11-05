#!/usr/bin/env python3
from sage.all import Matrix, vector, ZZ
import re
#bases_alice = ['X', 'X', 'X', 'Z', 'X', 'X', 'Z', 'X', 'X', 'X', 'X', 'Z', 'X', 'X', 'X', 'X', 'Z', 'Z', 'X', 'X', 'X', 'X', 'Z', 'Z', 'X', 'Z', 'X', 'Z', 'Z', 'Z', 'Z', 'X', 'Z', 'X', 'X', 'X', 'X', 'X', 'Z', 'X', 'Z', 'Z', 'Z', 'Z', 'X', 'X', 'Z', 'X', 'Z', 'Z', 'Z', 'Z', 'X', 'Z', 'Z', 'Z', 'Z', 'X', 'Z', 'X', 'Z', 'X', 'X', 'Z', 'Z', 'X', 'Z', 'Z', 'X', 'Z', 'X', 'Z', 'X', 'Z', 'X', 'X', 'X', 'X', 'Z', 'Z', 'Z', 'X', 'Z', 'Z', 'Z', 'Z', 'Z', 'X', 'X', 'Z', 'Z', 'Z', 'X', 'X', 'Z', 'X', 'Z', 'X', 'X', 'Z', 'X', 'X', 'X', 'Z', 'X', 'Z', 'Z', 'Z', 'Z', 'X', 'X', 'X', 'Z', 'X', 'X', 'X', 'X', 'Z', 'Z', 'Z', 'Z', 'X', 'Z', 'X', 'X', 'Z', 'Z', 'X', 'X', 'Z', 'Z', 'X', 'X', 'X', 'X', 'Z', 'Z', 'Z', 'X', 'Z', 'Z', 'Z', 'Z', 'Z', 'Z', 'X', 'X', 'X', 'X', 'Z', 'X', 'Z', 'X', 'X', 'X', 'Z', 'Z', 'Z', 'X', 'Z', 'X', 'Z', 'Z', 'X', 'Z', 'X', 'Z', 'Z', 'X', 'Z', 'X', 'X', 'X', 'Z', 'X', 'X', 'X', 'Z', 'Z', 'Z', 'Z', 'X', 'X', 'X', 'X', 'Z', 'Z', 'Z', 'X', 'X', 'Z', 'X', 'Z', 'Z', 'Z', 'X', 'Z', 'Z', 'Z', 'X', 'X', 'Z', 'X', 'X', 'Z', 'Z', 'X', 'Z', 'Z', 'X', 'X', 'Z', 'X', 'X', 'X', 'Z', 'X', 'X', 'X', 'X', 'X', 'X', 'Z', 'X', 'X', 'X', 'Z', 'Z', 'X', 'X', 'Z', 'X', 'X', 'X', 'Z', 'Z', 'Z', 'Z', 'X', 'X', 'Z', 'X', 'X', 'Z', 'X', 'X', 'X', 'Z', 'X', 'X', 'X', 'Z', 'X', 'X', 'X', 'Z']
#bits_alice =  [0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0]
#bases_bob  =  ['Z', 'X', 'X', 'Z', 'Z', 'Z', 'X', 'Z', 'Z', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'Z', 'Z', 'Z', 'X', 'Z', 'Z', 'X', 'X', 'Z', 'X', 'Z', 'X', 'X', 'X', 'Z', 'X', 'X', 'X', 'Z', 'Z', 'Z', 'X', 'X', 'X', 'X', 'X', 'Z', 'Z', 'Z', 'Z', 'Z', 'X', 'X', 'X', 'Z', 'Z', 'X', 'X', 'Z', 'Z', 'X', 'Z', 'Z', 'Z', 'Z', 'X', 'X', 'Z', 'Z', 'Z', 'X', 'X', 'X', 'Z', 'Z', 'Z', 'Z', 'X', 'Z', 'X', 'X', 'X', 'Z', 'Z', 'X', 'X', 'X', 'X', 'X', 'X', 'Z', 'X', 'Z', 'X', 'Z', 'X', 'Z', 'X', 'X', 'Z', 'X', 'X', 'X', 'X', 'Z', 'X', 'X', 'Z', 'X', 'Z', 'X', 'Z', 'X', 'Z', 'X', 'Z', 'Z', 'Z', 'Z', 'X', 'Z', 'X', 'X', 'Z', 'Z', 'X', 'Z', 'Z', 'Z', 'Z', 'Z', 'X', 'Z', 'X', 'Z', 'X', 'Z', 'X', 'X', 'Z', 'Z', 'Z', 'X', 'Z', 'X', 'X', 'X', 'Z', 'X', 'X', 'Z', 'X', 'X', 'X', 'Z', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'Z', 'X', 'Z', 'X', 'Z', 'Z', 'X', 'X', 'Z', 'X', 'Z', 'X', 'Z', 'X', 'X', 'X', 'Z', 'Z', 'Z', 'Z', 'X', 'X', 'Z', 'X', 'X', 'Z', 'Z', 'Z', 'Z', 'X', 'Z', 'Z', 'Z', 'Z', 'Z', 'X', 'X', 'Z', 'Z', 'X', 'Z', 'Z', 'X', 'Z', 'Z', 'Z', 'X', 'X', 'X', 'X', 'Z', 'Z', 'X', 'X', 'Z', 'Z', 'X', 'Z', 'X', 'Z', 'X', 'X', 'Z', 'Z', 'Z', 'X', 'X', 'Z', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'Z', 'X', 'Z', 'Z', 'X', 'X', 'Z', 'X', 'Z', 'Z', 'Z', 'Z', 'Z', 'X', 'Z', 'Z', 'X', 'Z']
#bits_bob  =   [0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0]

#d_bin = ""
# O len() é 256, como visto no bb84.py
#for i in range(len(bases_alice)): 
#    if bases_alice[i] == bases_bob[i]:
#        # Se as bases batem certo, guardamos o bit
#        d_bin += str(bits_alice[i])

# A correção crucial é aqui:
#d = int(d_bin, 2) # d = 163157290429967258856166843965534378824
def solve_lattice(p, a, b, c, d, m1, m2, m3):
    """
    Constrói e resolve a lattice para encontrar s0, s1, s2, s3.
    """
    print("\nA construir a lattice...")
    
    # 1. Calcular as constantes K1 e K2
    # K₁ = (1+d)·m₁ - m₂ (mod p)
    # K₂ = (1+d)·m₂ - m₃ - (d-c)·m₁ (mod p)
    
    K1 = ((1 + d) * m1 - m2) % p
    K2 = ((1 + d) * m2 - m3 - (d - c) * m1) % p

    # 2. Definir os coeficientes das nossas equações
    # Eq A: a*s0 + (b-a)*s1 + (c-b)*s2 + (d-c)*s3 ≡ K1 (mod p)
    # Eq B: 0*s0 +   a*s1 + (b-a)*s2 + (c-b)*s3 ≡ K2 (mod p)

    c_a0 = a
    c_a1 = (b - a) % p
    c_a2 = (c - b) % p
    c_a3 = (d - c) % p
    
    c_b0 = 0
    c_b1 = a
    c_b2 = (b - a) % p
    c_b3 = (c - b) % p

    # 3. Construir a Matriz (Lattice Basis)
    # Esta é a parte crucial. Usamos o método CVP (Closest Vector Problem).
    # A nossa lattice L é gerada pelas linhas da matriz M.
    # Um vetor na lattice é v = (s0, s1, s2, s3, k1*p + f_A(s), k2*p + f_B(s))
    # Estamos à procura de um vetor v que esteja "próximo" do vetor T = (0, 0, 0, 0, K1, K2).
    
    M = Matrix(ZZ, [
        [1, 0, 0, 0, c_a0, c_b0],
        [0, 1, 0, 0, c_a1, c_b1],
        [0, 0, 1, 0, c_a2, c_b2],
        [0, 0, 0, 1, c_a3, c_b3],
        [0, 0, 0, 0, p, 0],
        [0, 0, 0, 0, 0, p]
    ])
    
    # O nosso vetor alvo T
    T = vector(ZZ, [0, 0, 0, 0, K1, K2])

    # 4. Resolver a Lattice usando LLL + Babai
    M_LLL = M.LLL()
    
    # Algoritmo de Babai para CVP (Closest Vector Problem)
    # Encontrar o vetor na lattice mais próximo de T
    from sage.all import QQ
    
    # Resolver o sistema M_LLL * coef = T (aproximadamente)
    # Usamos divisão no espaço racional e arredondamos
    G, mu = M_LLL.gram_schmidt()
    coef = []
    t = T
    n = M_LLL.nrows()
    for i in range(n):
        # Projeção de t sobre o vetor de Gram-Schmidt
        c = (t * G[i]) / (G[i] * G[i])
        coef.append(round(c))
        t = t - round(c) * M_LLL[i]
    
    # Vetor da lattice mais próximo
    v_sol = sum(coef[i] * M_LLL[i] for i in range(n))
    
    print(f"Vetor alvo (T): {T}")
    print(f"Vetor da solução (v_sol): {v_sol}")

    # 5. Extrair a solução
    # O v_sol encontrado não é (s0, s1, ...), mas sim o vetor v = (s0, s1, s2, s3, v4, v5)
    # onde v4 ~= K1 e v5 ~= K2.
    # As nossas incógnitas são os 4 primeiros componentes.
    
    # Mas v_sol = (s0, s1, s2, s3, ...) NÃO é garantido.
    # Temos de encontrar o vetor de coeficientes 'c' tal que c * M_LLL = v_sol
    # e depois 'c' * M = v_real.
    # A forma mais fácil é resolver o sistema.
    
    # A saída de closest_vector() é o próprio vetor da lattice.
    s0 = v_sol[0]
    s1 = v_sol[1]
    s2 = v_sol[2]
    s3 = v_sol[3]
    
    # Os 's' podem sair negativos. O limite é 2**64.
    # Se s_i for negativo, é provável que seja (s_i_real - B), mas vamos verificar.
    # No chall.py, é randint(1, 2**64). Vamos assumir que são positivos.
    
    B = 2**64
    if not (0 < s0 < B and 0 < s1 < B and 0 < s2 < B and 0 < s3 < B):
         print("\nA solução encontrada está fora dos limites esperados (0, 2**64).")
         print("Isto pode acontecer se o 'closest_vector' não for a solução.")
         print("Uma alternativa é verificar os primeiros vetores da base LLL.")
         
         # O vetor (0,0,0,0, -K1, -K2) também deve ser testado.
         T_inv = vector(ZZ, [0, 0, 0, 0, -K1, -K2])
         
         # Algoritmo de Babai para o vetor invertido
         G = M_LLL.gram_schmidt()[0]
         coef_inv = []
         t_inv = T_inv
         for i in range(len(G)):
             c_inv = (t_inv * G[i]) / (G[i] * G[i])
             coef_inv.append(round(c_inv))
             t_inv = t_inv - round(c_inv) * M_LLL[i]
         
         v_sol_inv = sum(coef_inv[i] * M_LLL[i] for i in range(len(coef_inv)))
         s0_inv, s1_inv, s2_inv, s3_inv = v_sol_inv[0], v_sol_inv[1], v_sol_inv[2], v_sol_inv[3]
         
         if (0 < s0_inv < B and 0 < s1_inv < B and 0 < s2_inv < B and 0 < s3_inv < B):
             print("Encontrada solução com o vetor -T.")
             return s0_inv, s1_inv, s2_inv, s3_inv
         else:
             print("Nenhuma solução óbvia encontrada. O problema pode exigir outro tipo de lattice.")
             return None
    
    # Verificar se a solução está dentro dos limites
    print(f"\nValores encontrados: s0={s0}, s1={s1}, s2={s2}, s3={s3}")
    return s0, s1, s2, s3

# --- Função Principal ---
def main():
    p = 287876692519385687294901064478745169133
    a = 132538490704636058688740608443237236895
    b = 38377260243245066329208186026249007001
    c = 206172444918008613890240943595900127086
    d = 163157290429967258856166843965534378824
    measurements = [112191803829351766218879789773835272296, 146262447593996673654147940903299718988, 262643977426427509977095578682468011361]
    m1, m2, m3 = measurements
    # 3. Tentar resolver a lattice
    try:
        solution = solve_lattice(p, a, b, c, d, m1, m2, m3)
        
        if solution:
            s0, s1, s2, s3 = solution
            print(f"\n--- Solução Encontrada! ---")
            print(f"s0 = {s0}")
            print(f"s1 = {s1}")
            print(f"s2 = {s2}")
            print(f"s3 = {s3}")
            
            # 4. Construir a chave de cifragem
            key = (s0 << 384) | (s1 << 256) | (s2 << 128) | s3
            key_bytes = key.to_bytes(64, "little")
            
            print(f"\nChave de cifragem (int): {key}")
            print(f"Chave de cifragem (bytes): {key_bytes.hex()}")
            print("\nCom esta chave, podes agora decifrar o 'ciphertext' e 'ct'.")
            
    except NameError:
        print("\nErro: 'Matrix' ou 'vector' não definidos.")
        print("Por favor, executa este script usando 'sage -python nome_do_script.py'")
    except Exception as e:
        print(f"\nOcorreu um erro inesperado: {e}")

if __name__ == "__main__":
    main()

'''
# Testar d = todos os bits de Alice
d_alice_full = int(''.join(map(str, bits_alice)), 2)

# Testar d = todos os bits de Bob
d_bob_full = int(''.join(map(str, bits_bob)), 2)

# Testar d = XOR dos bits
d_xor = int(''.join(str(bits_alice[i] ^ bits_bob[i]) for i in range(256)), 2)

# Testar d = AND/OR/outras operações
d_and = int(''.join(str(bits_alice[i] & bits_bob[i]) for i in range(256)), 2)
d_or  = int(''.join(str(bits_alice[i] | bits_bob[i]) for i in range(256)), 2)

print(f"d_alice_full = {d_alice_full}")
print(f"d_bob_full   = {d_bob_full}")
print(f"d_xor        = {d_xor}")
print(f"d_and        = {d_and}")
print(f"d_or         = {d_or}")
python3 dRecovery.py 
d_alice_full = 56671514866526957080192048486514900142387895611843634263794115931792346663992
d_bob_full   = 22908307150687772680208828841077940795934550099415991184975528191680089001156
d_xor        = 36155575621823407876114060328053366883522439534275862689595672201918094426364
d_and        = 21712123197695660942143408499769737027400003088491881379586985960777170619392
d_or         = 57867698819519068818257468827823103910922442622767744069182658162695265045756
'''