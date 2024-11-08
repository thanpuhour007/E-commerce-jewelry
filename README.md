
---

# Jewelry E-commerce Project

A basic e-commerce platform for browsing and purchasing jewelry, built with Django.

## Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/thanpuhour007/E-commerce-jewelry.git
   cd jewelry-ecommerce
   ```

2. **Set up a virtual environment:**
   ```bash
   python -m venv venv
   # Activate the virtual environment:
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   - Copy `.env.example` to `.env` and update it with your database settings.

5. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser:**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the server:**
   ```bash
   python manage.py runserver
   ```

Visit [http://localhost:8000](http://localhost:8000) to access the site, and [http://localhost:8000/admin](http://localhost:8000/admin) for admin.

---

This version includes the essentials to set up and run your Django project locally.