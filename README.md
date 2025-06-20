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
inventory_management_system/
├── app/
│   ├── __init__.py           # Flask app initialization and blueprints
│   ├── admin.py             # Admin-specific routes and logic
│   ├── worker.py            # Worker-specific routes and logic
│   ├── models.py            # Database models
│   ├── utils.py             # Shared utilities
├── static/
│   ├── css/
│   │   └── style.css        # CSS file for styling
├── templates/
│   └── inventory_management.html  # Main HTML template
├── config.py                # Configuration settings
├── requirements.txt         # Python dependencies
├── run.py                   # Entry point to run the app
├── create_project_structure.py  # Script to generate project structure
└── README.md                # Project documentation
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

### ✅ Done!

Visit your app at: `http://<your-ec2-public-ip>:5000`

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

## 🤝 Contributing

Feel free to fork and contribute via pull requests. Suggestions for features like login authentication or request approval workflows are welcome!

---

## 📄 License

This project is licensed under the MIT License.

