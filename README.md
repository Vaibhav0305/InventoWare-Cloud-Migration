# 🚀 InventoWare Inventory Management System

This project is a Flask-based **Inventory Management System** (`invento-to-app`) with separate roles for admins and workers, deployed using a single SQLite database (`inventory.db`). It includes automated deployment with **Terraform**, **Docker**, and **GitHub Actions**.

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

invento-to-app/├── static/│   ├── login.css          # CSS for login page│   └── style.css          # General CSS for styling├── templates/│   ├── error.html         # Error page template│   ├── flask_wtf.html     # WTForms template (likely for CSRF)│   ├── index.html         # Main index template│   ├── login.html         # Login page template├── app.py                 # Main Flask application file├── inventory.db           # SQLite database file (generated, managed locally)├── requirements.txt       # Python dependencies├── Dockerfile             # Docker configuration for the app├── terraform/             # Terraform configuration for EC2│   ├── main.tf│   ├── variables.tf│   ├── outputs.tf├── .github/               # GitHub Actions configuration│   └── workflows/│       └── docker-push.yml├── InventoWare_Deployment_Steps.txt  # Deployment instructions├── gitattributes            # Git configuration file├── gitignore                # Git ignore file (excludes generated files)└── README.md                # Project documentation

*Note*: Generated files like `terraform.tfstate`, `terraform.tfstate.backup`, `.terraform/`, and `inventory.db` are excluded from version control via `.gitignore`.

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

☁️ Step 2: Provision EC2 Instance Using Terraform
cd terraform/
terraform init
terraform apply -var="key_name=<your-ec2-keypair-name>"

🔗 Step 3: SSH into Your EC2 Instance
ssh -i "<path-to-your-key.pem>" ec2-user@<your-ec2-public-ip>

🚀 Step 4: Pull and Run Docker Image on EC2
docker pull your-dockerhub-username/inventoware-app
docker run -d -p 5000:5000 --name inventoware your-dockerhub-username/inventoware-app


✅ Done!
Visit your app at: http://<your-ec2-public-ip>:5000

🛠️ Local Setup

Install Dependencies:pip install -r requirements.txt


Run the Application:python app.py


The app uses the existing inventory.db (or creates it if absent).
Access the app at http://127.0.0.1:5000/ (adjust based on app.py routes).




📖 Guides Included

📘 InventoWare_Deployment_Steps.txt – Manual deployment guide.


🤝 Contributing
Feel free to fork and contribute via pull requests. Suggestions for features like enhanced login authentication or request approval workflows are welcome!

📄 License
This project is licensed under the MIT License.```
