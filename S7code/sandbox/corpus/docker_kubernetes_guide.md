# Docker and Kubernetes: Container Orchestration

Containers standardize application packaging and deployment, while Kubernetes automates container lifecycle management at scale. Together they form the foundation of modern cloud-native infrastructure.

## Docker Fundamentals

### Images and Containers

A **Docker image** is an immutable snapshot of an application and its dependencies. A **container** is a running instance of an image.

```dockerfile
# Multi-stage Dockerfile for a Python application
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim AS runtime
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY src/ ./src/
USER nobody  # Don't run as root
CMD ["python", "-m", "src.main"]
```

Multi-stage builds minimize image size by excluding build tools from the final image.

### Key Dockerfile Instructions

```dockerfile
FROM ubuntu:22.04         # Base image
WORKDIR /app              # Set working directory
COPY src/ /app/src/       # Copy files
RUN apt-get install -y curl  # Execute during build
ENV DATABASE_URL=...      # Set environment variable
EXPOSE 8080               # Document port (doesn't publish)
HEALTHCHECK CMD curl -f http://localhost:8080/health
CMD ["python", "main.py"] # Default command
ENTRYPOINT ["python"]     # Override requires --entrypoint flag
```

### Docker Compose

```yaml
version: "3.9"
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/mydb
    depends_on:
      db:
        condition: service_healthy
    
  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_PASSWORD: password
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "postgres"]
      interval: 5s
      retries: 5

volumes:
  postgres_data:
```

## Kubernetes Architecture

### Control Plane Components

- **API Server**: Validates and processes REST API requests; central communication hub
- **etcd**: Distributed key-value store; source of truth for cluster state
- **Scheduler**: Assigns pods to nodes based on resource requirements
- **Controller Manager**: Runs reconciliation loops maintaining desired state

### Node Components

- **kubelet**: Agent on each node; ensures containers run per Pod spec
- **kube-proxy**: Maintains network rules for pod communication
- **Container runtime**: Runs containers (containerd, CRI-O)

### Core Resources

```yaml
# Deployment: manages ReplicaSet for stateless workloads
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
      - name: api
        image: myregistry/api:v1.2.3
        ports:
        - containerPort: 8000
        resources:
          requests:
            cpu: "100m"
            memory: "256Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
---
# Service: stable network endpoint for pods
apiVersion: v1
kind: Service
metadata:
  name: api
spec:
  selector:
    app: api
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
```

### Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-hpa
spec:
  scaleTargetRef:
    kind: Deployment
    name: api
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```
