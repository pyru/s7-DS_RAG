# Graph Neural Networks: Learning on Structured Data

Graph Neural Networks (GNNs) extend deep learning to graph-structured data, where relationships between entities are as important as the entities themselves. Applications span social networks, molecular property prediction, recommendation systems, and knowledge graphs.

## Why Graphs?

Many real-world phenomena are naturally relational:
- **Social networks**: Users connected by friendships, follows, interactions
- **Molecules**: Atoms connected by chemical bonds
- **Knowledge graphs**: Entities connected by semantic relations
- **Citation networks**: Papers connected by citations
- **Program analysis**: Control flow graphs, call graphs

Standard neural networks assume independent samples; CNNs assume grid-structured data. Graphs have irregular topology that requires specialized architectures.

## Message Passing: The GNN Framework

Most GNNs follow the **message passing** paradigm. For each layer:

1. **Aggregate** messages from neighboring nodes
2. **Update** node representation based on aggregated messages

```
mᵥ⁽ˡ⁾ = AGGREGATE({h_u⁽ˡ⁻¹⁾ : u ∈ N(v)})
h_v⁽ˡ⁾ = UPDATE(h_v⁽ˡ⁻¹⁾, m_v⁽ˡ⁾)
```

After L layers, each node's representation incorporates information from its L-hop neighborhood.

## Key GNN Architectures

### Graph Convolutional Network (GCN)

Spectral convolution simplified to a symmetric normalized adjacency:

```
H⁽ˡ⁺¹⁾ = σ(D̃⁻¹/²ÃD̃⁻¹/²H⁽ˡ⁾W⁽ˡ⁾)
```

Simple and effective but limited to transductive settings (requires full graph during training).

### GraphSAGE

Inductive learning: samples and aggregates from a fixed-size neighborhood. Supports unseen nodes at test time:

```python
def forward(self, x, edge_index):
    # Sample k neighbors, aggregate with mean/LSTM/pooling
    neighbors = sample_neighbors(edge_index, k=25)
    aggregated = self.aggregator(x[neighbors])
    return self.linear(torch.cat([x, aggregated], dim=1))
```

### Graph Attention Network (GAT)

Learns attention weights over neighbors rather than using fixed normalization:

```
αᵢⱼ = softmax(LeakyReLU(a · [Whᵢ || Whⱼ]))
h'ᵢ = σ(Σⱼ∈Nᵢ αᵢⱼ · Whⱼ)
```

Multi-head attention stabilizes training and captures diverse neighborhood patterns.

## Node, Edge, and Graph-Level Tasks

**Node classification**: Predict label for each node (semi-supervised learning on citation networks)

**Link prediction**: Predict whether an edge exists — used in recommendation, drug-drug interaction prediction

**Graph classification**: Map entire graph to a label — molecular property prediction, program analysis

**Graph generation**: Generate novel graphs — drug discovery, material design

## Over-Smoothing Problem

With many GNN layers, node representations converge to similar values (all nodes look the same). Practical GNNs use 2–4 layers. Mitigations:
- Residual connections
- JK-Net (Jumping Knowledge): aggregate representations from all layers
- GRAND: graph diffusion instead of stacking layers

## Scalability

Full-batch training becomes infeasible for billion-edge graphs. Sampling methods:
- **GraphSAGE**: Neighborhood sampling
- **GraphSAINT**: Graph sampling for mini-batches with unbiased estimation
- **Cluster-GCN**: Partition graph into clusters; train on subgraphs
- **PyG + DGL**: Major frameworks supporting both research and production-scale GNNs

## Applications in Practice

**AlphaFold 2**: GNN over predicted contact graphs for protein structure prediction
**Pinterest PinSage**: GraphSAGE for recommendation (3 billion nodes, 18 billion edges)
**Drug Discovery**: GNNs predict molecular toxicity, solubility, binding affinity
