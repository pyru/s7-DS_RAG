# Claude Shannon and Information Theory

Claude Elwood Shannon (1916–2001) was an American mathematician and electrical engineer widely regarded as the father of information theory. His landmark 1948 paper, "A Mathematical Theory of Communication," published in the Bell System Technical Journal, fundamentally changed how humans understand and transmit information.

## Key Contributions

Shannon introduced the concept of **entropy** as a measure of uncertainty or information content in a message. He defined entropy H for a discrete random variable X with possible outcomes {x₁, x₂, ..., xₙ} and probabilities {p₁, p₂, ..., pₙ} as:

H(X) = -∑ pᵢ log₂(pᵢ)

This measure quantifies the average amount of information contained in a message — or equivalently, the average number of bits required to encode it optimally. A coin flip has 1 bit of entropy; a six-sided die has approximately 2.58 bits.

## Channel Capacity Theorem

Shannon's most celebrated result is the **noisy channel coding theorem**, which states that for any communication channel with noise, there exists a maximum rate (the channel capacity C) at which information can be transmitted with arbitrarily low error probability. This capacity is:

C = B log₂(1 + S/N)

where B is the bandwidth in Hz and S/N is the signal-to-noise ratio. This formula, now called the Shannon-Hartley theorem, defines a fundamental limit that no coding scheme can exceed.

## Data Compression

Shannon also proved the **source coding theorem**: the minimum average number of bits needed to encode symbols from a source with entropy H is exactly H bits per symbol. This underpins all lossless compression algorithms — Huffman coding, arithmetic coding, and modern neural compressors all approach the Shannon entropy limit.

## Binary Digits and the Term "Bit"

Shannon is credited with coining the term **bit** (binary digit) to describe the fundamental unit of information. This concept — that all information could be reduced to sequences of 0s and 1s — became the bedrock of digital computing and telecommunications.

## Legacy

Shannon's work enabled modern digital communications, the Internet, mobile phones, streaming video, and data storage. His theory proved that error-correcting codes could achieve reliable communication over noisy channels — a result that seemed impossible before his proof. Beyond information theory, Shannon made contributions to cryptography (he proved that the one-time pad is the only unconditionally secure cipher), chess programming, and juggling theory.

Shannon spent most of his career at Bell Labs and MIT. He was known for riding unicycles through the halls of Bell Labs and building mechanical mice that could solve mazes — embodying the playful curiosity that characterized his scientific genius.
