
# 🚀 Cloud-Native CI/CD Pipeline with GitHub Actions, Jenkins, Terraform & Docker

A modern, automated CI/CD pipeline architecture designed for cloud-native deployments. This pipeline leverages GitHub Actions, Jenkins (booted on-demand via EC2), Terraform for infrastructure provisioning, and Docker for containerization. It also integrates quality scans, notifications, and rollback mechanisms.

---

## 🧰 Tech Stack

- **CI/CD:** GitHub Actions, Jenkins  
- **Infrastructure as Code:** Terraform  
- **Cloud Provider:** AWS (EC2, ALB, DNS)  
- **Containerization:** Docker, DockerHub  
- **Security & Quality:** SonarCloud, Trivy  
- **Monitoring:** Prometheus, Grafana  
- **Notifications:** Slack, Email  

---

## 🧱 Pipeline Overview

### 1. 🏗️ Preparation Phase

- **Checkout Code** (GitHub Actions)  
- **Configure AWS Credentials**  
- **Start Jenkins EC2 Instance**  
- **Wait for Jenkins Boot**  

### 2. 🐳 CI/CD via Jenkins

- **Build Docker Image**  
- **Push Docker Image to DockerHub**  
- **Trigger Jenkins Job**  
- **Poll Jenkins for Build Result**  
- **On Success:** Continue to deploy  
- **On Failure:** Rollback using last stable image  

### 3. 🏗️ Terraform Infra Provisioning

- **Checkout Terraform Code**  
- **Terraform Init & Plan**  
- **Conditional Apply**  
- **Terraform Output for ALB DNS/IPs**  

### 4. 🧪 Application Preparation & Testing

- **Checkout App Code**  
- **Lint App**  
- **Static Analysis:**  
  - SonarCloud Scan  
  - Trivy Security Scan  
- **Deploy via Bastion Host**  
- **Run Tests:**  
  - Smoke Test  
  - Load Test  
- **Switch ALB Target Group**  

### 5. 📣 Notifications

- **Email Report**  
- **Slack Notification**  

### 6. 🧹 Cleanup & Reporting

- **Stop Jenkins EC2 Instance**  
- **Email Notification**  

### 7. 📊 Monitoring & Observability

- **Prometheus & Grafana Dashboard**  
- **Alerts on Failure/Thresholds**  

---

## 🛠 Prerequisites

- AWS Account with EC2, IAM, and ALB permissions  
- DockerHub Account  
- Jenkins AMI or setup script for EC2  
- GitHub Repository with proper Secrets (AWS, DockerHub credentials)  
- Slack webhook (for notifications)  
- SonarCloud & Trivy configured for scans  

---

## 🛡️ Rollback Strategy

On Jenkins failure:
- Authenticate to DockerHub  
- Pull last stable Docker image  
- Redeploy using existing infrastructure  

---

## 📈 Monitoring Stack

- **Grafana:** Dashboards for traffic, latency, error rates  
- **Prometheus:** Metric collection  
- **Alerting:** Based on response times, success rates  

---

## 📬 Notifications

- **Slack:** Real-time channel alerts  
- **Email:** Reports after deployment or rollback  

---

## 🧹 Cleanup

Automatically stops Jenkins EC2 instance post-deployment to save cost.

---

## 📄 License

MIT License. See `LICENSE` for details.
