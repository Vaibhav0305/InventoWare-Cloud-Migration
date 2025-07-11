# 🚀 InventoWare Inventory Management System

This project is a Flask-based **Inventory Management System** with separate roles for admins and workers, deployed using a single database and modular Python files. It includes automated deployment capabilities with **Terraform**, **Docker**, and **GitHub Actions**.

---

## 📦 Prerequisites

- ✅ AWS account with an EC2 key pair created
- ✅ AWS CLI installed and configured (`aws configure`)
- ✅ Terraform installed ([Download Terraform](https://terraform.io))
- ✅ Docker installed ([Download Docker](https://docker.com))
- ✅ DockerHub account
- ✅ Python 3.12+ installed
- ✅ Pip installed for Python dependencies

---

## 📁 Project Structure

```
INVENTOWARE-CLOUD-MIGRATION/
│
├── .github/                          # GitHub Actions for CI/CD
│   └── workflows/
│       └── docker-push.yml           # Builds & pushes Docker image on push
│
├── invento-app/                      # Flask application directory
│   ├── static/                       # CSS and static assets
│   │   ├── login.css
│   │   └── style.css
│   ├── templates/                    # Jinja2 HTML templates
│   │   ├── error.html
│   │   ├── flask_wtf.html
│   │   ├── index.html
│   │   └── login.html
│   ├── app.py                        # Main Flask app
│   ├── inventory.db                  # SQLite database (ignored in .gitignore)
|   ├── app.log                            # Optional log file or directory
│   └── requirements.txt              # Python dependencies
│
├── terraform/                        # Terraform for provisioning AWS EC2
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│
├── Dockerfile                        # Docker config for app containerization
├── .gitattributes                    # Git config for file encoding/line-endings
├── .gitignore                        # Files to exclude from Git (env, db, cache)
└── README.md                         # Main project documentation

```

---

## 🚀 Auto Build & Push with GitHub Actions

This project is integrated with GitHub Actions to automatically:

- Build the Docker image on every push to `main`
- Push it to DockerHub as `your-dockerhub-username/inventoware-app`

### 🛠 How to Enable It

1. Go to your GitHub repo → **Settings → Secrets and variables → Actions**
2. Add the following **repository secrets**:

| Name                | Value                               |
|---------------------|-------------------------------------|
| `DOCKERHUB_USERNAME`| Your DockerHub username             |
| `DOCKERHUB_TOKEN`   | DockerHub Access Token ([link](https://hub.docker.com/settings/security)) |

---

## 🛠️ Manual Deployment Steps (Optional)

### 🔐 Step 1: Configure AWS Credentials
```bash
aws configure
```

### ☁️ Step 2: Provision EC2 Instance Using Terraform

```bash
cd terraform/
terraform init
terraform apply -var="key_name=<your-ec2-keypair-name>"
```

### 🔗 Step 3: SSH into Your EC2 Instance

```bash
ssh -i "<path-to-your-key.pem>" ec2-user@<your-ec2-public-ip>
```

### 🚀 Step 4: Pull and Run Docker Image on EC2

```bash
docker pull your-dockerhub-username/inventoware-app
docker run -d -p 5000:5000 --name inventoware your-dockerhub-username/inventoware-app
```

---

## 🛠️ Local Setup

1. **Generate Project Structure**:
   ```
   python create_project_structure.py
   ```
2. **Install Dependencies**:
   ```
   pip install -r requirements.txt
   ```
3. **Run the Application**:
   ```
   python run.py
   ```
   - The first run will create the SQLite database (`inventory.db`).
   - Access the app at `http://127.0.0.1:5000/admin/` or `http://127.0.0.1:5000/worker/` after implementing login logic.

---

## 📖 Guides Included

- 📘 `create_project_structure.py` – Script to set up the initial project structure.


---

## 📄 License

This project is licensed under the MIT License.

