import sys
from math import gcd
from itertools import product

def hex_to_bits(hex_str, known_bits):
    bits = []
    for byte in hex_str.replace('\n', '').replace(' ','').split(':'):
        for c in byte:
            if c == '?':
                bits.extend([None]*4)
            else:
                val = int(c, 16)
                bits.extend([(val >> 3) & 1, (val >> 2) & 1, (val >> 1) & 1, val & 1])
    return bits

def bits_to_int(bits):
    val = 0
    for b in reversed(bits):
        val = (val << 1) | (b if b is not None else 0)
    return val

def known_bits_mask(bits):
    mask = 0
    val = 0
    for i, b in enumerate(bits):
        if b is not None:
            mask |= 1 << i
            val |= (b & 1) << i
    return mask, val

def solve_k(p_bits, q_bits, d_bits, N, e):
    n = len(p_bits)
    p_mask, p_val = known_bits_mask(p_bits)
    q_mask, q_val = known_bits_mask(q_bits)
    d_mask, d_val = known_bits_mask(d_bits)
    
    for k in range(1, e):
        phi_approx = N - (p_val | ~p_mask) - (q_val | ~q_mask) + 1
        d_approx = (k * (N + 1) + 1) // e
        d_approx_bits = [(d_approx >> i) & 1 for i in range(len(d_bits))]
        match = True
        for i in range(len(d_bits)):
            if d_bits[i] is not None and d_approx_bits[i] != d_bits[i]:
                match = False
                break
        if match:
            return k
    return None

def solve_kp_kq(k, e):
    kp = pow(k, -1, e)
    kq = pow(k, -1, e)
    return kp, kq

def reconstruct_rsa(p_bits, q_bits, d_bits, N, e):
    n = len(p_bits)
    k = solve_k(p_bits, q_bits, d_bits, N, e)
    if k is None:
        raise ValueError("Could not determine k")
    kp, kq = solve_kp_kq(k, e)
    
    candidates = [{'p': 1, 'q': 1, 'd': (1 + k*(N - 1 + 1))//e}]
    for i in range(1, n):
        next_candidates = []
        for cand in candidates:
            p_prev = cand['p']
            q_prev = cand['q']
            d_prev = cand['d']
            for p_bit in [0, 1]:
                if p_bits[i] is not None and p_bit != p_bits[i]:
                    continue
                for q_bit in [0, 1]:
                    if q_bits[i] is not None and q_bit != q_bits[i]:
                        continue
                    p = p_prev | (p_bit << i)
                    q = q_prev | (q_bit << i)
                    if (p * q) & ((1 << (i+1)) -1) != N & (1 << (i+1)) -1:
                        continue
                    d = d_prev | ((k * (N - p - q + 1) + 1) // e) & (1 << i)
                    if d_bits[i] is not None and (d >> i) & 1 != d_bits[i]:
                        continue
                    next_candidates.append({'p': p, 'q': q, 'd': d})
        candidates = next_candidates
        if not candidates:
            break
    for cand in candidates:
        p = cand['p']
        q = cand['q']
        if p * q == N:
            return p, q
    return None, None

# Example usage with provided data (simplified for demonstration)
if __name__ == "__main__":
    # Parsing the provided hex data (truncated for example)
    p_hex = """e0:86:e8:e3:f0:03:bb:4e:36:a9:59:d?:79:f1:6?:?6
    ?b:e?:cd:??:1b:d1:da:?c:7?:35:87:b8:bc:?4:0f:?1
    dc:fd:f4:ff:1d:?d:b?:55:1e:47:e7:cf:07:a?:b6:10
    c0:67:ac:?6:?1:3?:49:d2:?f:aa:aa:d5:e3:24:1a:9b
    9a:fc:ae:??:20:dc:f7:??:db:4b:92:28:c0:85:42:65
    c7:97:86:1f:dc:c1:a9:81:6b:57:aa:af:98:?0:9?:76
    b2:1d:0b:?2:8?:f3:dc:?7:e5:e6:f9:85:?5:1b:79:d8
    ?3:9?:67:b0:94:23:63:c3:e1:c?:?b:27:4c:1e:82:79"""
    q_hex = """?0:6e:8f:f0:c3:e9:a5:7a:6f:2?:07:8b:83:16:c7:8d
    29:a7:69:?3:?a:3d:?2:44:13:e2:c4:6?:e2:b8:0a:9c
    22:1c:c2:8f:?4:20:58:cc:4b:?b:df:7?:?8:6?:2f:13
    99:d3:8?:e0:?2:d?:a9:5d:b4:a?:8a:8a:2e:d0:ae:2a
    49:?9:c7:76:??:b9:b8:5f:6d:ca:af:eb:e8:52:96:69
    e5:8a:4e:d7:b?:f?:6a:1c:8d:?3:b?:0?:?6:5e:72:78
    ce:71:c7:ac:fd:2a:c?:9d:a2:?7:f0:c7:a4:?c:d?:9a
    9?:c1:88:?7:a3:af:3?:3c:a6:?6:d4:?5:23:9c:?1:79"""
    d_hex = """02:c9:8d:?8:ee:b7:?a:??:99:74:44:70:bb:?f:?1:?9
    d7:5f:b9:90:c?:42:30:55:8?:6?:2?:?8:35:79:98:1e
    f?:1a:b2:c5:f?:8f:f6:9?:??:7f:0c:?9:d9:cf:3a:6a
    ??:?9:99:31:d?:27:??:40:81:4d:00:71:c?:f0:05:d3
    12:f1:5?:50:70:?1:3e:3f:d3:2c:39:28:16:6f:3e:a1
    f5:1?:7?:e7:a5:62:80:45:3?:5?:3d:?a:?7:5a:b?:7d
    b0:56:c?:52:1?:?d:22:bc:7d:50:3e:e8:76:ec:?6:?8
    11:?c:75:1c:d2:91:4d:1e:54:5?:c7:d8:d2:f8:95:71
    ?2:0?:c1:5b:73:6b:69:74:68:7b:27:58:38:5e:fa:8a
    f7:?0:ac:fc:de:52:0d:8f:ed:f6:f2:fd:d3:d8:af:05
    51:4?:45:5d:?7:43:83:b9:8b:ab:a?:?2:fc:74:1?:6?
    d7:2?:b4:89:55:4b:ff:??:ea:d9:?b:ff:e5:5?:cb:31
    d0:96:92:0e:39:f1:?8:?a:05:?6:47:26:8c:fb:71:f2
    ?e:ea:?2:dd:2d:9b:00:18:3e:45:13:6a:c8:5?:60:5e
    ?e:f6:?2:4?:db:5e:01:8e:07:a?:af:60:1b:7a:77:56
    b0:8a:d5:fe:?c:73:50:62:6?:71:f4:cd:f?:4a:40:31"""
    N_hex = """a8:c6:26:e1:8c:59:46:2a:2a:e5:b5:91:03:de:25:c6
    75:c1:a9:7c:0c:c4:a4:98:ea:38:bf:56:95:69:73:d9
    1f:26:83:2b:7e:3a:e7:95:34:7f:03:09:f2:bf:f1:bd
    ce:b4:96:e7:e5:ce:c7:df:41:0e:9d:af:b2:47:d2:a8
    6b:7c:9a:06:be:10:c1:71:b0:90:43:0e:82:30:86:d1
    78:52:12:8d:dd:19:b6:10:41:db:87:a4:ea:1c:2e:36
    92:a3:55:34:93:44:c7:de:0c:12:2b:85:c5:ce:8f:e4
    91:4d:59:33:1e:9f:9a:1d:07:fc:29:4c:45:59:a8:35
    d2:e2:0d:2d:dd:c5:66:52:b9:e2:bd:9e:bf:3d:7c:a3
    45:8e:ec:65:7f:99:f3:f3:7b:4b:5a:2f:d6:db:78:6f
    25:61:fc:6f:2e:5b:0e:43:f4:b5:29:28:44:a1:e0:52
    20:e8:b6:e7:1e:ef:66:30:46:c5:0e:bc:d3:73:e1:c9
    8a:a9:72:09:c3:65:e5:0b:d1:b9:b0:6f:de:ce:03:a6
    f3:33:5a:7e:44:f1:b9:8f:46:52:20:be:c8:e4:2a:55
    46:1b:c3:b9:46:4c:54:07:06:df:20:5d:de:71:68:36
    68:ea:ef:62:29:7a:4c:ca:bd:ef:6c:3f:de:20:d4:31"""
    e = 65537
    
    p_bits = hex_to_bits(p_hex, {})
    q_bits = hex_to_bits(q_hex, {})
    d_bits = hex_to_bits(d_hex, {})
    N = bits_to_int(hex_to_bits(N_hex, {}))
    
    p, q = reconstruct_rsa(p_bits, q_bits, d_bits, N, e)
    if p and q:
        print(f"Recovered p: {p}\nRecovered q: {q}")
    else:
        print("Failed to recover p and q")
