# Data Compression and Coding Theory

Data compression reduces the number of bits required to represent information, exploiting statistical redundancy in data. Shannon's source coding theorem provides the theoretical minimum: no lossless code can compress below the entropy of the source.

## Lossless Compression

Lossless compression guarantees perfect reconstruction of the original data.

### Huffman Coding

Huffman coding assigns shorter codes to more frequent symbols. Given symbol probabilities, it constructs an optimal prefix-free code:

1. Create leaf nodes for each symbol with its probability
2. Repeatedly merge the two lowest-probability nodes
3. Assign 0/1 to left/right branches

Example: A=0.5, B=0.25, C=0.125, D=0.125
- A: "0" (1 bit), B: "10" (2 bits), C: "110" (3 bits), D: "111" (3 bits)
- Average: 0.5×1 + 0.25×2 + 0.125×3 + 0.125×3 = 1.75 bits/symbol
- Entropy: H = 1.75 bits/symbol (Huffman is optimal here)

### Arithmetic Coding

Arithmetic coding encodes an entire message as a single number in [0,1), approaching the entropy limit with negligible overhead. The encoder maintains a shrinking interval based on cumulative symbol probabilities.

### LZ77 and Derivative Algorithms

LZ77 (Ziv and Lempel, 1977) replaces repeated substrings with (offset, length) pointers into a sliding window. The basis for:
- DEFLATE (used in gzip, ZIP, PNG): LZ77 + Huffman coding
- Zstandard (Facebook): DEFLATE successor with significantly better speed/ratio
- LZO: Optimized for speed over compression ratio

## Dictionary Compression

LZ78 builds an explicit dictionary of encountered phrases. LZW (used in GIF) maintains this dictionary dynamically.

**Brotli** (Google): Reference implementation for HTTP/2 compression. Pre-seeded with a static dictionary of common web content, achieving 20-26% better compression than gzip for HTML/CSS/JavaScript.

## Run-Length Encoding

RLE replaces repeated values with (value, count) pairs: AAABBBBBCC → A3B5C2. Effective for data with long runs (fax images, bitmap graphics).

## Entropy Coding in Modern Contexts

**ANS (Asymmetric Numeral Systems)**: Recent entropy coding method combining Huffman's speed with arithmetic coding's ratio. Used in Zstandard and HEVC video compression.

## Lossy Compression

Lossy compression removes information that is perceptually insignificant.

### JPEG (Images)

1. Convert RGB to YCbCr (separate luminance from chrominance)
2. Downsample chroma channels (human vision is less sensitive to color detail)
3. Apply 8×8 Discrete Cosine Transform (DCT)
4. Quantize DCT coefficients (this is the loss step)
5. Entropy code with Huffman

### MP3 (Audio)

Psychoacoustic model identifies frequencies that are perceptually masked by louder neighboring frequencies, then allocates fewer bits to inaudible components.

### Neural Compression

Deep learning compressors (HiFiC for images, Encodec for audio) learn optimal representations end-to-end, outperforming hand-engineered codecs at high compression ratios. They use variational autoencoders or normalizing flows with learned entropy models.

## Compression and Shannon's Theorem

Shannon's source coding theorem sets the theoretical minimum for lossless compression: the expected code length cannot be less than the entropy H(X) bits per symbol. Modern entropy coders (ANS, arithmetic) approach this limit with overhead of less than 0.001 bits per symbol.

For lossy compression, the **rate-distortion theorem** characterizes the tradeoff: at any rate R, the minimum achievable distortion D(R) follows a decreasing function determined by the source distribution.
