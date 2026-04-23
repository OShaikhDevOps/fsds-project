
# Fullstack Project

This repository contains a small Fullstack ML project: a trained classification model, a FastAPI backend for inference, a Streamlit frontend, containerization assets, and Infrastructure-as-Code to provision resources.

**Quick Start**
- **Backend:** install dependencies and run FastAPI

```bash
python -m venv .venv
source .venv/bin/activate   # or fullstack\\Scripts\\Activate.ps1 on Windows
pip install -r backend/requirements.txt
uvicorn inference:app --reload --host 0.0.0.0 --port 8000
```

- **Frontend:** run Streamlit

```bash
pip install -r frontend/requirements.txt
streamlit run frontend/streamlit_app.py
```

**Repository Layout**
- **Model:** [backend/model](backend/model) — contains `best_fruit_model.pt` (large; typically mounted at runtime)
- **Backend:** [backend/inference.py](backend/inference.py) — FastAPI app exposing `/` and `/predict`
- **Frontend:** [frontend/streamlit_app.py](frontend/streamlit_app.py) — lightweight UI for uploading images
- **Containerization:** [microservices/Dockerfile-backend](microservices/Dockerfile-backend), [.dockerignore](.dockerignore), [.gitignore](.gitignore)
- **IAC:** [iac/](iac/) — Terraform modules and root stacks (see `iac/modules/ec2`)
- **Nanoservices (Lambdas):** [nanoservices/inference_lambda.py](nanoservices/inference_lambda.py)

**1) Model**
- **Location:** [backend/model/best_fruit_model.pt](backend/model/best_fruit_model.pt)
- **Notes:** The model is an Ultralytics/Torch `.pt` file. It may be large — avoid committing model artifacts to git (the repo `.gitignore` already ignores `/backend/model/*.pt`). For production, store the model in S3 and download at startup or mount it into the container.

**2) Frontend**
- **What:** Streamlit UI for uploading images and showing predictions.
- **Run:** `streamlit run frontend/streamlit_app.py`
- **Deps:** See [frontend/requirements.txt](frontend/requirements.txt)

**3) Backend**
- **What:** FastAPI service implemented in [backend/inference.py](backend/inference.py).
- **Endpoints:**
  - `GET /` — health + model info
  - `POST /predict` — accepts an image file and returns `label`, `confidence`, `class_idx`, `inference_ms`
- **Run (dev):** `uvicorn inference:app --reload --host 0.0.0.0 --port 8000`
- **Notes:** The app prefers `ultralytics.YOLO` for model loading but will fall back to `torch.load` if needed. Ensure `ultralytics` and `torch` are installed in production images.

**4) Containerization**
- **Dockerfile (backend):** [microservices/Dockerfile-backend](microservices/Dockerfile-backend)
- **Build:**
  ```bash
  docker build -f microservices/Dockerfile-backend -t backend:latest .
  ```
- **Run (recommended):** mount the model at runtime to avoid large images
  ```bash
  docker run --rm -p 8000:8000 -v $(pwd)/backend/model:/app/backend/model backend:latest
  ```
- **Note:** `ultralytics`/`torch` increase image size; consider using GPU-ready images or pushing to ECR and running on ECS/GKE with proper resource limits.

**5) Infrastructure-as-Code (IAC)**
- **Path:** `iac/` — contains Terraform modules (`iac/modules/ec2`, `iac/ecr`, etc.).
- **EC2 module:** `iac/modules/ec2` picks a Canonical Ubuntu AMI and exposes variables:
  - `instance_type` (default `t3.micro`) — Free Tier friendly
  - `subnet_id` — optional; pass your subnet to launch into
  - `vpc_security_group_ids` — attach existing SGs
  - Outputs include `private_ip` and `public_ip`
- **Apply example:**
  ```bash
  terraform init
  terraform apply -var="subnet_id=subnet-0d166116426494b77" -var='vpc_security_group_ids=["sg-087d8b3b2626c2682"]'
  ```

**6) Nanoservice (Lambdas)**
- **Path:** [nanoservices/inference_lambda.py](nanoservices/inference_lambda.py)
- **Notes:** The lambda provides a lightweight inference option. Packaging must include dependencies (use Lambda layers or build a deployment package). For heavy deps like `torch`, prefer an ECS/EKS solution or use a smaller model or a container-based Lambda (AWS Lambda container images with larger size limits).

**7) High Availability & Resilience**
- **API layer:** run backend instances behind an Application Load Balancer (ALB) with health checks and an Auto Scaling Group (ASG) across multiple AZs.
- **Containers:** use ECS/Fargate or EKS with replicas, PodDisruptionBudgets, and horizontal autoscaling.
- **Model storage:** store models in S3 and cache locally on the instance/container; use versioned keys and lifecycle rules.
- **State & storage:** use managed databases (RDS with Multi-AZ) or S3 for artifacts. Avoid storing critical state on instance disks.
- **Networking:** place resources in private subnets, expose only necessary endpoints via ALB and API Gateway. Use security groups and NACLs.
- **Observability:** add CloudWatch metrics, logs, X-Ray/tracing, and alerts. Use health checks, circuit breakers, and graceful shutdowns.
- **CI/CD:** build container images in CI, push to registry (ECR), and deploy via Terraform/CD pipelines (CodePipeline / GitHub Actions).

**Useful files**
- [backend/inference.py](backend/inference.py)
- [backend/requirements.txt](backend/requirements.txt)
- [frontend/streamlit_app.py](frontend/streamlit_app.py)
- [microservices/Dockerfile-backend](microservices/Dockerfile-backend)
- [iac/modules/ec2/main.tf](iac/modules/ec2/main.tf)
- [iac/modules/ec2/variables.tf](iac/modules/ec2/variables.tf)

---
If you want, I can:
- add a `CONTRIBUTING.md` with development steps,
- add GitHub Actions to build & push images to ECR,
- or pin Terraform variables for a reproducible environment. Which would you like next?
