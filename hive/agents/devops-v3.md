# CI/CD for AI, Model Deployment, A/B Testing ML, Canary/Blue-Green — v3

> Production ML infrastructure reference. Updated 2026.

---

## 1. ML Pipeline CI/CD

### GitHub Actions — Basic ML Pipeline

```yaml
# .github/workflows/ml-pipeline.yml
name: ML Training Pipeline

on:
  push:
    branches: [main, 'features/**']
  schedule:
    # Weekly retraining
    - cron: '0 2 * * 0'

env:
  MODEL_REGISTRY: mlflow://${{ secrets.MLFLOW_HOST }}
  AWS_REGION: us-east-1

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install pytest pytest-cov
      - run: pytest tests/ --cov=src/

  validate-data:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate dataset statistics
        run: python scripts/validate_data.py
        env:
          DATASET_URI: ${{ secrets.DATASET_S3_URI }}
      # Data drift check: compare stats with reference
      - name: Check for data drift
        run: python scripts/drift_check.py

  train:
    needs: [test, validate-data]
    runs-on: gpu-large
    permissions:
      contents: read
      id-token: write  # for OIDC
    steps:
      - uses: actions/checkout@v4
      - name: Authenticate to AWS
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_TRAINING_ROLE_ARN }}
          aws-region: ${{ env.AWS_REGION }}
      - name: Run training
        run: python scripts/train.py
        env:
          MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_TRACKING_URI }}
      - name: Register model
        run: python scripts/register_model.py
        env:
          MODEL_REGISTRY: ${{ env.MODEL_REGISTRY }}

  deploy-staging:
    needs: [train]
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - run: echo "Deploying to staging via ArgoCD sync"
```

### Argo Workflows (Kubernetes-native ML Pipelines)

```yaml
# argo-workflow-ml.yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: ml-training-
spec:
  entrypoint: ml-pipeline
  ttlSecondsAfterCompletion: 86400

  templates:
  - name: ml-pipeline
    dag:
      tasks:
      - name: data-validation
        template: validate-data
      - name: train-model
        template: train
        depends: data-validation
      - name: evaluate-model
        template: evaluate
        depends: train-model
      - name: register-model
        template: register
        depends: evaluate-model
      - name: deploy-staging
        template: deploy-staging
        depends: register-model

  - name: validate-data
    script:
      image: python:3.11-slim
      command: [python]
      source: |
        from evidently.dashboard import Dashboard
        from evidently.tabs import DataDriftTab
        # Validate data drift

  - name: train
    nodeSelector:
      nvidia.com/gpu: "1"
    script:
      image: nvidia/cuda:12.4-cudnn9-runtime-ubuntu22.04
      command: [python]
      source: |
        import torch
        # Training logic

  - name: register
    script:
      image: python:3.11-slim
      command: [python]
      source: |
        import mlflow
        mlflow.register_model(...)
```

### Kubeflow Pipelines vs ZenML vs Metaflow

| Feature | Kubeflow | ZenML | Metaflow |
|---|---|---|---|
| Infrastructure | Kubernetes only | Agnostic (K8s, local, cloud) | Cloud-native (AWS, GCP, Azure) |
| UI | Native Katib + Pipelines | Dashboard via frontend | Native (Holistics) |
| Step caching | Yes | Yes | Yes |
| Integration depth | Deep K8s/GPU | Clean abstraction | Deep AWS |
| Learning curve | Steep | Moderate | Low |
| Best for | Large orgs, K8s-native | Modern teams, flexibility | Data scientists, AWS shops |

---

## 2. Model Registry & MLOps Lifecycle

### MLflow Model Registry

```python
import mlflow
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Register new model version
result = mlflow.register_model(
    model_uri=f"runs:/{run_id}/model",
    name="recommender-v1"
)

# Add metadata
client.set_model_version_tag("recommender-v1", result.version, "environment", "production")
client.set_model_version_tag("recommender-v1", result.version, "accuracy", 0.94)
client.set_model_version_tag("recommender-v1", result.version, "latency_p99_ms", 45)

# Transition stages
client.transition_model_version_stage(
    name="recommender-v1",
    version=result.version,
    stage="Staging"
)
```

**Stage lifecycle**: None → Staging → Production → Archived

**Model lineage**: MLflow captures:
- Training dataset URI + version (via DVC)
- Parameters and config
- Metrics
- Code snapshot (git commit hash)
- Environment (conda env / Docker image digest)

### DVC (Data Version Control)

```bash
# Track data alongside code
dvc init
dvc add data/raw/training.csv
git add data/raw/training.csv.dvc
git commit -m "add training data v2.3"

# Register data version
dvc push -r remote-storage

# Reproduce pipeline
dvc repro training_pipeline.dvc

# Compare runs
dvc metrics diff --gpu
```

### Weights & Biases Artifacts

```python
import wandb

run = wandb.init(project="recommender", job_type="training")

artifact = wandb.Artifact("model", type="model")
artifact.add_file("model.pt")
run.log_artifact(artifact)

# Download specific version for serving
run.use_artifact("model:v5")
```

---

## 3. Model Serving

### Triton Inference Server

Gold standard for production ML inference. Supports TensorRT, ONNX, PyTorch, TensorFlow, custom backends.

```protobuf
// config.pbtxt for Triton
name: "recommender"
platform: "pytorch_libtorch"
max_batch_size: 128
input [
  { name: "INPUT0" data_type: TYPE_INT64 dims: [ -1 ] }
]
output [
  { name: "OUTPUT0" data_type: TYPE_FP32 dims: [ -1 ] }
]
instance_group [{ kind: KIND_GPU count: 2 }]
dynamic_batching {
  preferred_batch_size: [32, 64, 128]
  max_queue_delay_microseconds: 100
}
```

```bash
# Serve with Triton
tritonserver --model-repository=/models \
  --grpc-port=8001 \
  --http-port=8000 \
  --metrics-port=8002
```

### FastAPI + Triton Integration

```python
from fastapi import FastAPI
import torch
import tritonclient.http as tritonhttpclient

app = FastAPI()
client = tritonhttpclient.InferenceServerClient("localhost:8000")

@app.post("/predict")
async def predict(request: PredictRequest):
    inputs = [
        tritonhttpclient.InferInput("INPUT0", [len(request.ids)], "INT64")
    ]
    inputs[0].set_data_from_numpy(np.array(request.ids))
    
    outputs = [tritonhttpclient.InferRequestedOutput("OUTPUT0")]
    
    results = client.infer("recommender", inputs, outputs=outputs)
    scores = results.as_numpy("OUTPUT0")
    
    return {"scores": scores.tolist()}
```

### ONNX Runtime — Quantization

```python
import onnx
from onnxruntime.quantization import quantize_dynamic, QuantType

# Dynamic INT8 quantization
quantized_model = quantize_dynamic(
    "model.onnx",
    "model_int8.onnx",
    weight_type=QuantType.QInt8
)
# Typically 2-4x throughput improvement, ~1-2% accuracy loss
```

### Performance Targets

| Model size | Hardware | Throughput (req/s) | P50 latency | P99 latency |
|---|---|---|---|---|
| 7B LLM (FP16) | 1x A100 80GB | 15-30 | 65ms | 150ms |
| 7B LLM (INT8) | 1x A100 80GB | 50-80 | 20ms | 50ms |
| 13B LLM (FP16) | 1x A100 80GB | 5-12 | 85ms | 200ms |
| Embedding (384d) | CPU | 2000+ | 1ms | 5ms |
| Recommender NN | GPU (T4) | 5000+ | 0.5ms | 2ms |

---

## 4. Containerization for GPU Workloads

```dockerfile
# pytorch-cuda.Dockerfile
FROM nvidia/cuda:12.4.1-cudnn-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Multi-stage: build stage
FROM nvidia/cuda:12.4.1-cudnn-devel-ubuntu22.04 as builder
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Runtime stage
FROM nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04
COPY --from=builder /install /usr/local
COPY app/ /app
WORKDIR /app

RUN useradd -m model-server && \
    chown -R model-server:model-server /app
USER model-server

ENV TORCH_CUDA_ARCH_LIST="8.0;8.6;8.9;9.0"
CMD ["python", "serve.py"]
```

**Image size optimization tips:**
- Use `python:slim` or `python:3.11-slim` as base when CUDA not needed in build stage
- Multi-stage builds: compile in large image, copy artifacts to slim runtime
- Delete apt cache: `rm -rf /var/lib/apt/lists/*`
- Typical GPU serving image: 8-15GB (includes CUDA, cuDNN). Use distroless for minimal

---

## 5. Canary Deployments for ML

### Argo Rollouts

```yaml
# rollout-ml.yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: recommender-model
spec:
  replicas: 10
  strategy:
    canary:
      steps:
      - setWeight: 5
      - pause: {duration: 10m}  # Monitor for 10 min
      - analysis:
          templates:
          - templateName: ml-metrics
          args:
          - name: service-name
            value: recommender-model-canary
      - setWeight: 25
      - pause: {duration: 30m}
      - setWeight: 50
      - pause: {duration: 60m}
      - setWeight: 100
      trafficRouting:
        istio:
          virtualService:
            name: recommender-vsvc
            routes:
            - primary
      canaryMetadata:
        labels:
          track: canary
      stableMetadata:
        labels:
          track: stable
```

### Analysis Template — ML-Specific Metrics

```yaml
# analysis-template.yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: ml-metrics
spec:
  args:
  - name: service-name
  metrics:
  - name: request-success-rate
    interval: 1m
    successCondition: result[0] >= 0.99
    failureLimit: 3
    provider:
      prometheus:
        address: http://prometheus:9090
        query: |
          sum(rate(http_requests_total{service="{{args.service-name}}",code!~"5.."}[1m]))
          /
          sum(rate(http_requests_total{service="{{args.service-name}}"}[1m]))

  - name: prediction-latency-p99
    interval: 2m
    successCondition: result[0] <= 100
    failureLimit: 2
    provider:
      prometheus:
        query: |
          histogram_quantile(0.99,
            rate(prediction_latency_seconds_bucket{service="{{args.service-name}}"}[2m])
          )

  - name: accuracy-drift
    interval: 5m
    successCondition: result[0] >= 0.93
    failureLimit: 1
    provider:
      prometheus:
        query: |
          accuracy_last_24h{service="{{args.service-name}}"}
```

**ML-specific canary metric**: Shadow accuracy — run canary model on a sample of stable traffic, compare outputs without affecting user experience.

### Flagger (Istio)

```yaml
# flagger-hpa.yaml
apiVersion: flagger.app/v1beta1
kind: MetricTemplate
metadata:
  name: latency
spec:
  provider:
    type: prometheus
    address: http://prometheus:9090
  query: |
    histogram_quantile(0.99,
      sum(rate(istio_request_duration_milliseconds_bucket{
        destination=~"{{ .Target.Name }}.*"
      }[5m])) by (le)
    / 1000
```

---

## 6. Blue-Green Deployments

### Architecture

```
LB → [Green (active)] [Blue (idle)]

Switch: Update LB weight 0% Blue → 100% Blue, then scale down Green
Rollback: Switch LB weight back to Green (instant)
```

### ECS Blue-Green (AWS CodeDeploy)

```yaml
# ecs-codedeploy.json
{
  "runtimeConfig": {
    "taskDefinition": "arn:aws:ecs:us-east-1:123456:task-definition/recommender:5"
  },
  "deploymentStrategy": {
    "type": "BLUE_GREEN_2",
    "deploymentWorkflow": "ALLOCATE_CONCURRENT",
    "terminationWorkflow": "DEPLOYMENT_COMPLETE"
  }
}
```

### Feature Flags vs Infrastructure Swap

| Approach | Latency | Rollback | Use when |
|---|---|---|---|
| Feature flag (LaunchDarkly/Statsig) | Instant | Instant | Model variant selection, A/B |
| DNS weighted routing (Route53) | Minutes (TTL) | Minutes | Major infra changes |
| Load balancer weight (ALB) | Real-time | Instant | Canary percentage |
| Infrastructure swap (ECS blue-green) | 2-5 min | 2-5 min | Container image changes |

---

## 7. A/B Testing for ML

### Experiment Design

```python
import numpy as np
from scipy import stats

def ab_test_sample_size(baseline_rate: float, mde: float, alpha: float = 0.05, power: float = 0.8):
    """Calculate required sample size per variant."""
    from statsmodels.stats.power import zt_indepsn_proportion
    effect_size = abs(baseline_rate - (baseline_rate + mde)) / np.sqrt(baseline_rate * (1 - baseline_rate))
    result = zt_indepsn_proportion.get_solver_derived(alpha=alpha, power=power)(effect_size)
    return int(result * 2)

n = ab_test_sample_size(baseline_rate=0.02, mde=0.005)
print(f"Need {n:,} samples per variant")  # ~62,000 per variant
```

### Multi-Arm Bandits (Thompson Sampling)

```python
import numpy as np
from numpy.random import beta

class ThompsonSampler:
    def __init__(self, n_arms):
        self.n_arms = n_arms
        self.alpha = np.ones(n_arms)  # successes + 1
        self.beta = np.ones(n_arms)   # failures + 1
        
    def select_arm(self):
        samples = beta(self.alpha, self.beta)
        return np.argmax(samples)
    
    def update(self, arm, reward):
        self.alpha[arm] += reward
        self.beta[arm] += 1 - reward
    
    def expected_ctr(self):
        return self.alpha / (self.alpha + self.beta)
```

### Statsig / LaunchDarkly in ML Routing

```python
# Feature flag-based model routing
import statsig

statsig.initialize(os.getenv("STATSIG_KEY"))

user = {
    "userID": user_id,
    "email": email,
    "country": country
}

# Get model assignment
model_variant = statsig.get_config(user, "model_version", {
    "default": "v3-stable"
}).get("model_version", "v3-stable")

# Log conversion event for stats
statsig.log_event(user_id, "prediction_made", value=1.0, metadata={
    "model": model_variant,
    "latency_ms": latency
})
statsig.log_event(user_id, "conversion", value=revenue, metadata={
    "model": model_variant
})

# Run A/B analysis in Statsig
result = statsig.get_experiment(user, "recommender_model_experiment")
```

### Metrics to Track

| Metric Type | Examples | Why |
|---|---|---|
| Business | Conversion rate, revenue, retention | True success indicators |
| Engagement | Click-through, dwell time, shares | Engagement signals |
| ML quality | Accuracy, MAP@K, AUC | Model health |
| System | Latency, error rate, throughput | Reliability |
| Distribution | Prediction drift, score distribution | Model stability |

---

## 8. Shadow Mode / Dark Launches

```python
import asyncio

async def shadow_predict(user_id: str, input_data: dict):
    """Run new model alongside stable model, compare outputs."""
    stable_result = await stable_model.predict(input_data)
    
    # Dark launch: run candidate model in background
    candidate_task = asyncio.create_task(candidate_model.predict(input_data))
    
    try:
        candidate_result = await asyncio.wait_for(candidate_task, timeout=5.0)
    except asyncio.TimeoutError:
        candidate_result = None
        log_warning("Shadow model timeout for user", user_id)
    
    # Compare outputs (no user impact)
    if candidate_result:
        divergence = compute_divergence(stable_result.embeddings, candidate_result.embeddings)
        log_shadow_metrics(user_id, divergence, latency=candidate_result.latency)
    
    return stable_result  # Always return stable model result
```

Monitor divergence distribution over time. If candidate diverges >10% of requests significantly, alert before full rollout.

---

## 9. Observability — ML Dashboards

### Prometheus Metrics for ML

```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server

prediction_latency = Histogram(
    'prediction_latency_seconds',
    'Latency of model predictions',
    ['model_version', 'endpoint'],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

predictions_total = Counter(
    'predictions_total',
    'Total predictions made',
    ['model_version', 'status']  # status: success, error, timeout
)

model_accuracy = Gauge(
    'model_realtime_accuracy',
    'Real-time accuracy (rolling window)',
    ['model_version']
)

prediction_confidence = Histogram(
    'prediction_confidence_distribution',
    'Distribution of prediction confidence scores',
    ['model_version'],
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
)
```

### Grafana Dashboard Panels

1. **Request rate** (rate(predictions_total[5m]))
2. **P50/P95/P99 latency** (histogram_quantile)
3. **Error rate** (rate(predictions_total{status="error"}[5m]))
4. **Real-time accuracy** (rolling evaluation)
5. **Prediction score distribution** (histogram)
6. **Feature drift** (population stability index over time)
7. **Canary vs stable delta** (when doing progressive rollout)

### Data Drift Detection

**Evidently AI**:

```python
from evidently.dashboard import Dashboard
from evidently.tabs import DataDriftTab, NumDriftTab, CatDriftTab

report = Dashboard(tabs=[
    DataDriftTab(),
    NumDriftTab(),
    CatDriftTab()
])

report.run(
    reference_data=reference_df,
    current_data=current_df,
    column_mapping=ColumnMapping()
)
report.save("drift_report.html")
```

**NannyML (post-production monitoring)**:
- CBPE (Concrete Behavioral Predictive Error) — estimate accuracy without ground truth
- DDE (Data Drift Ensemble) — multivariate drift detection
- Univariate drift — PSI, KL divergence per feature

**Population Stability Index (PSI)**:

```python
import numpy as np

def psi(expected: np.ndarray, actual: np.ndarray, buckets=10):
    def calc_psi(expected, actual, buckets):
        breakpoints = np.percentile(expected, np.linspace(0, 100, buckets + 1))
        exp_counts = np.histogram(expected, breakpoints)[0] / len(expected)
        act_counts = np.histogram(actual, breakpoints)[0] / len(actual)
        # Avoid division by zero
        exp_counts = np.where(exp_counts == 0, 0.0001, exp_counts)
        act_counts = np.where(act_counts == 0, 0.0001, act_counts)
        psi = (exp_counts - act_counts) * np.log(exp_counts / act_counts)
        return np.sum(psi)
    return calc_psi(expected, actual, buckets)

# PSI < 0.1: no significant drift
# PSI 0.1-0.2: moderate drift, investigate
# PSI > 0.2: significant drift, consider retraining
```

---

## 10. Infrastructure — Kubernetes GPU Scheduling

```yaml
# gpu-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: training-job
spec:
  template:
    spec:
      nodeSelector:
        nvidia.com/gpu: "1"
      containers:
      - name: trainer
        image: pytorch-training:latest
        resources:
          limits:
            nvidia.com/gpu: "2"
            memory: "32Gi"
          requests:
            nvidia.com/gpu: "2"
            memory: "16Gi"
        env:
        - name: NVIDIA_VISIBLE_DEVICES
          value: "0,1"
      tolerations:
      - key: "gpu"
        operator: "Exists"
        effect: "NoSchedule"
      # Allow spot instances (preemptible)
      tolerations:
      - key: "node.kubernetes.io/preemptible"
        operator: "Exists"
```

**Karpenter for auto-scaling GPU nodes**:
```yaml
# karpenter nodepool
apiVersion: karpenter.sh/v1beta1
kind: NodePool
metadata:
  name: gpu-pool
spec:
  template:
    spec:
      requirements:
      - key: nvidia.com/gpu
        operator: Exists
      - key: node.kubernetes.io-instance-type
        operator: In
        values: [p4d.24xlarge, p5.48xlarge]
      limits:
        capacity: 10
      ttlSecondsAfterEmpty: 120
  disruption:
    consolidationPolicy: WhenUnderutilized
```

---

## 11. Security & Compliance

### Model Poisoning Prevention

1. **Training data validation**: Verify data provenance, checksum, scan for anomalies
2. **Artifact signing**: Sign model artifacts with Cosign, verify before loading
3. **Model provenance**: MLflow + SigMF for model lineage documentation
4. **Sandbox execution**: Run untrusted models in isolated containers with seccomp/AppArmor

### RBAC for Model Registry

```yaml
# OPA Rego policy for model registry access
package mlflow.rbac

default allow = false

allow if {
    input.user.role == "ml-engineer"
    input.action in {"read", "deploy"}
}

allow if {
    input.user.role == "admin"
}
```

### GDPR for Model Outputs

- Right to explanation: Use SHAP/LIME for feature attribution on predictions
- Right to erasure: Model deletion requests — implement model version deletion with audit trail
- Data minimization: Don't train on PII unless necessary; use differential privacy

---

## 12. Cost Optimization

### Quantization Overview

| Method | Size reduction | Accuracy loss | Speedup |
|---|---|---|---|
| FP16 (baseline) | 1x | — | 1x |
| INT8 (per-tensor) | 2x | 1-3% | 2-4x |
| INT8 (per-channel) | 2x | 0.5-2% | 2-3x |
| INT4 (AWQ/GPTQ) | 4x | 2-5% | 4-6x |
| INT4 (GGUF/llama.cpp) | 4x | 2-5% | 4-8x |
|蒸馏 Distillation | Variable | 1-5% | Depends |

### GGUF / llama.cpp for Local Inference

```bash
# Quantize a model to Q4_K_M
./quantize models/llama-3-8b-integer-f32.gguf \
  models/llama-3-8b-integer-q4_k_m.gguf Q4_K_M

# Serve with llama.cpp server
./server -m models/llama-3-8b-integer-q4_k_m.gguf \
  -c 8192 -ngl 35 --host 0.0.0.0 --port 8080
```

### Speculative Decoding

Draft model (small) generates tokens → target model verifies in parallel. 2-3x faster token generation on average with quality preserved.

```python
# vLLM speculative decoding config
from vllm import LLM, SamplingParams

llm = LLM(
    model="meta-llama/Llama-3-8B-Instruct",
    speculative_config=SpeculativeConfig(
        predictor_model="llama-3-1.3B-Instruct",  # Draft model
        num_speculative_tokens=5
    )
)
```

### Batch Caching for Cost Reduction

Group requests by similarity (same system prompt, similar user context). Process in batches with shared KV cache. vLLM's continuous batching handles this automatically.

---

*Generated 2026-04-22 — Requires web search for latest benchmark numbers and tool versions*
