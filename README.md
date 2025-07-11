# 🚀 InventoWare Inventory Management System

InventoWare is a Flask-based **Inventory Management System** supporting admin and worker roles, powered by **modular Python**, **Dockerized deployments**, and **cloud-native DevOps tooling**.

This project features a fully automated, **blue-green CI/CD pipeline** using **GitHub Actions**, **Jenkins**, **Terraform**, and AWS — integrated with a complete monitoring stack, security scanning, and dynamic DNS routing.

---

## 📦 Prerequisites

* ✅ AWS account with EC2 key pair and IAM credentials
* ✅ AWS CLI configured (`aws configure`)
* ✅ Terraform installed ([Download](https://www.terraform.io/downloads.html))
* ✅ Docker installed and running ([Download](https://www.docker.com/get-started))
* ✅ GitHub & DockerHub accounts
* ✅ Python 3.12+ and `pip` installed

---

## 📁 Project Structure

```
INVENTOWARE-CLOUD-MIGRATION/
│
├── .github/                          # GitHub Actions for CI pipeline
│   └── workflows/
│       └── ci.yml                    # Starts Jenkins CD job + rollback logic
│
├── app/invento-app/                 # Flask inventory app
│   ├── static/                      # CSS assets
│   ├── templates/                   # HTML templates (Jinja2)
│   ├── app.py                       # Main Flask app
│   └── requirements.txt             # Python dependencies
│
├── infra/terraform/                 # AWS infrastructure provisioning
│   ├── main.tf                      # EC2, VPC, ALB, TGs
│   ├── variables.tf
│   └── outputs.tf
│
├── Dockerfile                       # Dockerfile for app container
├── Jenkinsfile                      # Jenkins CD pipeline with blue-green deploy
├── README.md                        # You are here ✅
└── .gitignore
```

---

## 🔀 End-to-End Pipeline (CI + CD)

### 💡 Overview

| Stage          | Tool                      | Description                                                              |
| -------------- | ------------------------- | ------------------------------------------------------------------------ |
| **CI**         | GitHub Actions            | Lint, Trivy scan, SonarCloud scan, triggers Jenkins CD                   |
| **CD**         | Jenkins on EC2            | Terraform provisioning, app deployment, health check, blue-green routing |
| **Monitoring** | Prometheus, Grafana, Loki | Tracks app logs, metrics, and system health                              |
| **Security**   | Trivy, SonarCloud         | Scans Docker image & code for vulnerabilities                            |
| **Rollback**   | DockerHub `:previous` tag | Fallback if deployment fails or smoke test fails                         |

---

## 🔷 Blue-Green Deployment

* Each deployment targets **blue** or **green** EC2 group
* ALB listener switches to new target group post-deploy
* Ensures **zero downtime** & rollback safety

> Deployment color is passed via a Jenkins `DEPLOYMENT_COLOR` parameter (auto-configurable)

---

## 🔐 Secure Infrastructure

* 🕪️ Bastion Host with **SSH tunneling** to access private EC2s
* 🔑 Credentials stored via **Jenkins Credentials Manager** and **GitHub Secrets**
* 📦 Docker image scanning via **Trivy**
* 🧲 Code quality enforced via **SonarCloud**

---

## 📊 Monitoring Stack

The system includes a full monitoring suite:

| Tool              | Purpose                    |
| ----------------- | -------------------------- |
| **Grafana**       | Visualization & dashboards |
| **Prometheus**    | Metrics collection         |
| **Loki**          | Log aggregation            |
| **cAdvisor**      | Container stats            |
| **Node Exporter** | System-level metrics       |

Dashboards display CPU, memory, request latency, status codes, and more.

---

## 🧪 Health, Smoke & Load Testing

* `/health` endpoint tested after deploy
* Smoke test via `curl`
* Load test via `k6` (Grafana)

---

## 🚀 CI Pipeline with GitHub Actions

### 🛠 Setup Repository Secrets

| Secret Name               | Purpose                                  |
| ------------------------- | ---------------------------------------- |
| `DOCKERHUB_USERNAME`      | DockerHub username                       |
| `DOCKERHUB_TOKEN`         | DockerHub token                          |
| `JENKINS_USER`            | Jenkins basic auth username              |
| `JENKINS_API_TOKEN`       | Jenkins API token                        |
| `JENKINS_URL`             | Jenkins base URL (e.g. `http://ip:8080`) |
| `JENKINS_INSTANCE_ID`     | EC2 instance ID for Jenkins server       |
| `JENKINS_JOB_NAME`        | Name of the Jenkins job                  |
| `AWS_ACCESS_KEY_ID`       | AWS IAM credentials                      |
| `AWS_SECRET_ACCESS_KEY`   | AWS IAM credentials                      |
| `EMAIL_USERNAME/PASSWORD` | For SMTP notifications                   |

---

## 🛠️ Manual Deployment (Optional)

1. **Provision Infra**:

   ```bash
   cd infra/terraform/
   terraform init
   terraform apply -var="key_name=<your-key-name>"
   ```

2. **SSH & Deploy**:

   ```bash
   ssh -i "<key.pem>" ec2-user@<public-ip>
   docker run -d -p 5000:5000 your-dockerhub-username/inventoware-app
   ```

---

## 💻 Local Setup

```bash
# Clone repo and install dependencies
cd app/invento-app/
pip install -r requirements.txt

# Run locally
python app.py
# Visit http://127.0.0.1:5000/
```

---

## 📩 Notifications

* Slack alerts: deployment summary, status, instance IPs, ALB URL
* Email reports: attached SonarCloud and Trivy scan reports

---

## 📄 License

This project is licensed under the **MIT License**.
