# 🛒 Ecommerce_django

A robust, scalable, and feature-rich eCommerce application built with Django. This project is designed with a service-oriented approach, separating core business logic into distinct apps for seamless online shopping, order management, and payment processing.

## ✨ Key Features

* **Modular Architecture:** Separated Django apps for `products`, `orders`, and `payments` to maintain clean and scalable code.
* **Advanced Product Management:** Includes built-in pagination and robust product filtering capabilities.
* **High-Performance Caching:** Integrated **Redis** cache for lightning-fast product retrieval and optimized database querying.
* **Cloud-Ready Deployment:** Pre-configured for cloud environments with AWS Elastic Beanstalk (`.ebextensions`) and AWS RDS database support.
* **Automated Workflows:** GitHub Actions (`.github/workflows`) configured for automated builds and testing.

## 🛠️ Tech Stack

* **Backend:** Python, Django
* **Database:** SQLite3 (Local Development) / AWS RDS (Production)
* **Caching:** Redis
* **Deployment & Hosting:** AWS Elastic Beanstalk, Procfile (Heroku-compatible)
* **Version Control:** Git & GitHub

## 📂 Project Structure

```text
Ecommerce_django/
├── ecommerce_application/  # Core Django project settings and configurations
├── products/               # Product catalog, filtering, and Redis caching service
├── orders/                 # Order management and processing service
├── payments/               # Payment gateway integration service
├── .ebextensions/          # AWS Elastic Beanstalk configuration files
├── .github/workflows/      # CI/CD pipelines
├── manage.py               # Django command-line utility
├── populate.py             # Script to populate initial database records
└── requirements.txt        # Project dependencies

```

## 🚀 Local Development Setup

Follow these steps to get your development environment set up locally.

### Prerequisites

* Python 3.8+
* Redis server (must be running locally for caching features to work)
* Git

### Installation Steps

**1. Clone the repository**

```bash
git clone https://github.com/Seeramsetty-Lakshmi-Venkata-Akhil/Ecommerce_django.git
cd Ecommerce_django

```

**2. Create and activate a virtual environment**

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

```

**3. Install dependencies**

```bash
pip install -r requirements.txt

```

**4. Ensure Redis is running**
Make sure your local Redis server is active on the default port (`6379`).

**5. Apply database migrations**

```bash
python manage.py makemigrations
python manage.py migrate

```

**6. Populate initial data (Optional)**
If you want to load sample data into your database, run the provided population script:

```bash
python populate.py

```

**7. Run the development server**

```bash
python manage.py runserver

```

The application will now be accessible at `[http://127.0.0.1:8000/](http://127.0.0.1:8000/)`.

## ☁️ Deployment

This project is built to be easily deployable to cloud providers:

* **AWS Elastic Beanstalk:** Utilize the included `.elasticbeanstalk` and `.ebextensions` directories for seamless AWS deployment.
* **AWS RDS:** Configure your production environment variables to point to your AWS RDS instance instead of the local `db.sqlite3`.
* **Procfile:** Included for PaaS providers like Heroku or Render.

## 📄 License

This project is licensed under the **Apache-2.0 License**. See the `LICENSE` file for more details.

---

*Developed by 
Lakshmi Venkata Akhil
https://www.google.com/search?q=https%3A%2F%2Fgithub.com%2FSeeramsetty-Lakshmi-Venkata-Akhil
