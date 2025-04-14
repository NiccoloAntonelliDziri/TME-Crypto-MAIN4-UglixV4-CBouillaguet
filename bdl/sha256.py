class ChainingValue(list):
    def __init__(self, x):
        if isinstance(x, str):
            l = [int(chunk, 16) for chunk in [x[8*i:8*(i+1)] for i in range(8)]]
            super().__init__(l)
        else:
            super().__init__(x)

    def __add__(self, x):
        return [ (self[i] + x[i]) & 0xffffffff for i in range(8) ]

    def __iadd__(self, x):
        for i in range(8):
            self[i] = (self[i] + x[i]) & 0xffffffff
        return self

    def hex(self):
        return "".join(map(lambda x: "{0:08x}".format(x), self))


class MessageBlock(bytearray):
   pass


def F(input_h, m):
    """
    Fonction de compression
    """
    def Ch(x,y,z):
        return z ^ (x & (y ^ z))

    def Maj(x,y,z):
        return ((x | y) & z) | (x & y)

    def S(x, n):
        return (((x & 0xffffffff) >> (n & 31)) | (x << (32 - (n & 31)))) & 0xffffffff

    def R(x, n):
        return (x & 0xffffffff) >> n

    def MessageExpansion(m):
        def Gamma0(x):
            return S(x, 7) ^ S(x, 18) ^ R(x, 3)

        def Gamma1(x):
            return S(x, 17) ^ S(x, 19) ^ R(x, 10)

        W = []
        for i in range(0,16):
            W.append( (m[4*i]<<24) + (m[4*i+1]<<16) + (m[4*i+2]<<8) + m[4*i+3])
        for i in range(16,64):
            W.append( (Gamma1(W[i - 2]) + W[i - 7] + Gamma0(W[i - 15]) + W[i - 16]) & 0xffffffff )
        return W

    # apply round function 64 times
    def RND(a,b,c,d,e,f,g,h,i,ki):
        def Sigma0(x):
            return S(x, 2) ^ S(x, 13) ^ S(x, 22)

        def Sigma1(x):
            return S(x, 6) ^ S(x, 11) ^ S(x, 25)

        t0 = h + Sigma1(e) + Ch(e, f, g) + ki + W[i];
        t1 = Sigma0(a) + Maj(a, b, c);
        d += t0;
        h  = t0 + t1;
        return (d & 0xffffffff), (h & 0xffffffff)

    # clone input chaining value
    h = ChainingValue(input_h)
    W = MessageExpansion(m)

    h[3], h[7] = RND(h[0],h[1],h[2],h[3],h[4],h[5],h[6],h[7],0,0x428a2f98);
    h[2], h[6] = RND(h[7],h[0],h[1],h[2],h[3],h[4],h[5],h[6],1,0x71374491);
    h[1], h[5] = RND(h[6],h[7],h[0],h[1],h[2],h[3],h[4],h[5],2,0xb5c0fbcf);
    h[0], h[4] = RND(h[5],h[6],h[7],h[0],h[1],h[2],h[3],h[4],3,0xe9b5dba5);
    h[7], h[3] = RND(h[4],h[5],h[6],h[7],h[0],h[1],h[2],h[3],4,0x3956c25b);
    h[6], h[2] = RND(h[3],h[4],h[5],h[6],h[7],h[0],h[1],h[2],5,0x59f111f1);
    h[5], h[1] = RND(h[2],h[3],h[4],h[5],h[6],h[7],h[0],h[1],6,0x923f82a4);
    h[4], h[0] = RND(h[1],h[2],h[3],h[4],h[5],h[6],h[7],h[0],7,0xab1c5ed5);
    h[3], h[7] = RND(h[0],h[1],h[2],h[3],h[4],h[5],h[6],h[7],8,0xd807aa98);
    h[2], h[6] = RND(h[7],h[0],h[1],h[2],h[3],h[4],h[5],h[6],9,0x12835b01);
    h[1], h[5] = RND(h[6],h[7],h[0],h[1],h[2],h[3],h[4],h[5],10,0x243185be);
    h[0], h[4] = RND(h[5],h[6],h[7],h[0],h[1],h[2],h[3],h[4],11,0x550c7dc3);
    h[7], h[3] = RND(h[4],h[5],h[6],h[7],h[0],h[1],h[2],h[3],12,0x72be5d74);
    h[6], h[2] = RND(h[3],h[4],h[5],h[6],h[7],h[0],h[1],h[2],13,0x80deb1fe);
    h[5], h[1] = RND(h[2],h[3],h[4],h[5],h[6],h[7],h[0],h[1],14,0x9bdc06a7);
    h[4], h[0] = RND(h[1],h[2],h[3],h[4],h[5],h[6],h[7],h[0],15,0xc19bf174);
    h[3], h[7] = RND(h[0],h[1],h[2],h[3],h[4],h[5],h[6],h[7],16,0xe49b69c1);
    h[2], h[6] = RND(h[7],h[0],h[1],h[2],h[3],h[4],h[5],h[6],17,0xefbe4786);
    h[1], h[5] = RND(h[6],h[7],h[0],h[1],h[2],h[3],h[4],h[5],18,0x0fc19dc6);
    h[0], h[4] = RND(h[5],h[6],h[7],h[0],h[1],h[2],h[3],h[4],19,0x240ca1cc);
    h[7], h[3] = RND(h[4],h[5],h[6],h[7],h[0],h[1],h[2],h[3],20,0x2de92c6f);
    h[6], h[2] = RND(h[3],h[4],h[5],h[6],h[7],h[0],h[1],h[2],21,0x4a7484aa);
    h[5], h[1] = RND(h[2],h[3],h[4],h[5],h[6],h[7],h[0],h[1],22,0x5cb0a9dc);
    h[4], h[0] = RND(h[1],h[2],h[3],h[4],h[5],h[6],h[7],h[0],23,0x76f988da);
    h[3], h[7] = RND(h[0],h[1],h[2],h[3],h[4],h[5],h[6],h[7],24,0x983e5152);
    h[2], h[6] = RND(h[7],h[0],h[1],h[2],h[3],h[4],h[5],h[6],25,0xa831c66d);
    h[1], h[5] = RND(h[6],h[7],h[0],h[1],h[2],h[3],h[4],h[5],26,0xb00327c8);
    h[0], h[4] = RND(h[5],h[6],h[7],h[0],h[1],h[2],h[3],h[4],27,0xbf597fc7);
    h[7], h[3] = RND(h[4],h[5],h[6],h[7],h[0],h[1],h[2],h[3],28,0xc6e00bf3);
    h[6], h[2] = RND(h[3],h[4],h[5],h[6],h[7],h[0],h[1],h[2],29,0xd5a79147);
    h[5], h[1] = RND(h[2],h[3],h[4],h[5],h[6],h[7],h[0],h[1],30,0x06ca6351);
    h[4], h[0] = RND(h[1],h[2],h[3],h[4],h[5],h[6],h[7],h[0],31,0x14292967);
    h[3], h[7] = RND(h[0],h[1],h[2],h[3],h[4],h[5],h[6],h[7],32,0x27b70a85);
    h[2], h[6] = RND(h[7],h[0],h[1],h[2],h[3],h[4],h[5],h[6],33,0x2e1b2138);
    h[1], h[5] = RND(h[6],h[7],h[0],h[1],h[2],h[3],h[4],h[5],34,0x4d2c6dfc);
    h[0], h[4] = RND(h[5],h[6],h[7],h[0],h[1],h[2],h[3],h[4],35,0x53380d13);
    h[7], h[3] = RND(h[4],h[5],h[6],h[7],h[0],h[1],h[2],h[3],36,0x650a7354);
    h[6], h[2] = RND(h[3],h[4],h[5],h[6],h[7],h[0],h[1],h[2],37,0x766a0abb);
    h[5], h[1] = RND(h[2],h[3],h[4],h[5],h[6],h[7],h[0],h[1],38,0x81c2c92e);
    h[4], h[0] = RND(h[1],h[2],h[3],h[4],h[5],h[6],h[7],h[0],39,0x92722c85);
    h[3], h[7] = RND(h[0],h[1],h[2],h[3],h[4],h[5],h[6],h[7],40,0xa2bfe8a1);
    h[2], h[6] = RND(h[7],h[0],h[1],h[2],h[3],h[4],h[5],h[6],41,0xa81a664b);
    h[1], h[5] = RND(h[6],h[7],h[0],h[1],h[2],h[3],h[4],h[5],42,0xc24b8b70);
    h[0], h[4] = RND(h[5],h[6],h[7],h[0],h[1],h[2],h[3],h[4],43,0xc76c51a3);
    h[7], h[3] = RND(h[4],h[5],h[6],h[7],h[0],h[1],h[2],h[3],44,0xd192e819);
    h[6], h[2] = RND(h[3],h[4],h[5],h[6],h[7],h[0],h[1],h[2],45,0xd6990624);
    h[5], h[1] = RND(h[2],h[3],h[4],h[5],h[6],h[7],h[0],h[1],46,0xf40e3585);
    h[4], h[0] = RND(h[1],h[2],h[3],h[4],h[5],h[6],h[7],h[0],47,0x106aa070);
    h[3], h[7] = RND(h[0],h[1],h[2],h[3],h[4],h[5],h[6],h[7],48,0x19a4c116);
    h[2], h[6] = RND(h[7],h[0],h[1],h[2],h[3],h[4],h[5],h[6],49,0x1e376c08);
    h[1], h[5] = RND(h[6],h[7],h[0],h[1],h[2],h[3],h[4],h[5],50,0x2748774c);
    h[0], h[4] = RND(h[5],h[6],h[7],h[0],h[1],h[2],h[3],h[4],51,0x34b0bcb5);
    h[7], h[3] = RND(h[4],h[5],h[6],h[7],h[0],h[1],h[2],h[3],52,0x391c0cb3);
    h[6], h[2] = RND(h[3],h[4],h[5],h[6],h[7],h[0],h[1],h[2],53,0x4ed8aa4a);
    h[5], h[1] = RND(h[2],h[3],h[4],h[5],h[6],h[7],h[0],h[1],54,0x5b9cca4f);
    h[4], h[0] = RND(h[1],h[2],h[3],h[4],h[5],h[6],h[7],h[0],55,0x682e6ff3);
    h[3], h[7] = RND(h[0],h[1],h[2],h[3],h[4],h[5],h[6],h[7],56,0x748f82ee);
    h[2], h[6] = RND(h[7],h[0],h[1],h[2],h[3],h[4],h[5],h[6],57,0x78a5636f);
    h[1], h[5] = RND(h[6],h[7],h[0],h[1],h[2],h[3],h[4],h[5],58,0x84c87814);
    h[0], h[4] = RND(h[5],h[6],h[7],h[0],h[1],h[2],h[3],h[4],59,0x8cc70208);
    h[7], h[3] = RND(h[4],h[5],h[6],h[7],h[0],h[1],h[2],h[3],60,0x90befffa);
    h[6], h[2] = RND(h[3],h[4],h[5],h[6],h[7],h[0],h[1],h[2],61,0xa4506ceb);
    h[5], h[1] = RND(h[2],h[3],h[4],h[5],h[6],h[7],h[0],h[1],62,0xbef9a3f7);
    h[4], h[0] = RND(h[1],h[2],h[3],h[4],h[5],h[6],h[7],h[0],63,0xc67178f2);

    # feedworward
    h += input_h
    return h


class sha256:
    block_size = 64  # 512-bit message block

    def __init__(self, s=None, IV="6a09e667bb67ae853c6ef372a54ff53a510e527f9b05688c1f83d9ab5be0cd19"):
        # bloc de message en cours
        self.data = MessageBlock()
        # valeur de chainage actuelle
        self.digest = ChainingValue(IV)
        # compteur d'octets hachés en tout
        self.count = 0
        if s:
            self.update(s)


    def compress(self):
        """
        invoque la fonction de compression.
        Met à jour la valeur de chainage et vide le bloc en cours
        """
        self.digest = F(self.digest, self.data)
        self.data = MessageBlock()

    def update(self, buffer):
        """
        Hache le contenu de ``buffer``.
        """
        # update hashed byte count
        self.count += len(buffer)

        buffer_size = len(buffer)
        buffer_idx = 0

        # un bloc déjà entamé est présent dans "data"
        if self.data:
            # on copie ``i`` octets du ``buffer`` dedans
            i = min(buffer_size, self.block_size - len(self.data))
            self.data.extend(buffer[:i])
            buffer_size -= i
            buffer_idx += i

            if len(self.data) == self.block_size:
                self.compress()
            else:
                # pas de quoi remplir un bloc complet : exit
                return

        # ici, le bloc "en cours" est vide
        # tant qu'on peut former des blocs complets, on les compresse
        while buffer_size >= self.block_size:
            self.data = MessageBlock(buffer[buffer_idx:buffer_idx + self.block_size])
            buffer_size -= self.block_size
            buffer_idx += self.block_size
            self.compress()

        # copie la fin du buffer dans le bloc "en cours"
        self.data = MessageBlock(buffer[buffer_idx:])

    def _finalize(self):
        """
        Applique le bourrage.
        """
        # il y a toujours la place d'ajouter un octet
        self.data.append(0x80)

        # bourre la fin avec des 0
        space = self.block_size - len(self.data)
        self.data.extend([0] * space)

        # y a-t-il la place d'ajouter le compteurs de bits hachés ?
        if space < 8:
            self.compress()
            self.data = MessageBlock([0] * self.block_size)

        # écrit le compteur par-dessus les zéros à la fin
        self.count *= 8
        for i in range(8):
            self.data[63 - i] = (self.count >> (8 * i)) & 0xff
        self.compress()


    def hexdigest(self):
        """
        Renvoie l'empreinte des données hachées jusque-là.
        """
        self._finalize()
        return self.digest.hex()


def test():
    a_str = "just a test string".encode()

    assert 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855' == sha256().hexdigest()
    assert 'd7b553c6f09ac85d142415f857c5310f3bbbe7cdd787cce4b985acedd585266f' == sha256(a_str).hexdigest()
    assert 'fbe80d3195306da12154ae2245b530425f933cfdc3fd40ec9f70f88c7da9e797' == sha256(a_str*4).hexdigest()
    assert '8113ebf33c97daa9998762aacafe750c7cefc2b2f173c90c59663a57fe626f21' == sha256(a_str*7).hexdigest()

    s = sha256(a_str)
    s.update(a_str)
    assert '03d9963e05a094593190b6fc794cb1a3e1ac7d7883f0b5855268afeccc70d461' == s.hexdigest()

    s = sha256(a_str)
    s.update(a_str)
    s.update(a_str)
    s.update(a_str)
    assert 'fbe80d3195306da12154ae2245b530425f933cfdc3fd40ec9f70f88c7da9e797' == s.hexdigest()

if __name__ == "__main__":
    test()


