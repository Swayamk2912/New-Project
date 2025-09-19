# Freelancer Marketplace

This is a Django-based Freelancer Marketplace application.

## Setup Instructions

Follow these steps to get the development environment up and running.

### Prerequisites

*   Docker and Docker Compose (recommended for development)
*   Python 3.x (if not using Docker)
*   pip (if not using Docker)

### 1. Using Docker (Recommended)

The easiest way to get started is by using Docker Compose.

1.  **Build and run the Docker containers:**
    ```bash
    docker-compose up --build
    ```
    This command will:
    *   Build the Docker images (if not already built).
    *   Start the database service.
    *   Start the Django application service.

2.  **Run database migrations:**
    Once the containers are running, execute migrations inside the Django container:
    ```bash
    docker-compose exec web python FreelancerM/manage.py migrate
    ```

3.  **Create a superuser (optional, for admin access):**
    ```bash
    docker-compose exec web python FreelancerM/manage.py createsuperuser
    ```
    Follow the prompts to create an admin user.

4.  **Access the application:**
    The application should now be accessible at `http://localhost:8000`.

### 2. Local Setup (Without Docker)

If you prefer to run the application directly on your machine:

1.  **Install Python dependencies:**
    Navigate to the project root and install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run database migrations:**
    ```bash
    python FreelancerM/manage.py migrate
    ```

3.  **Create a superuser (optional, for admin access):**
    ```bash
    python FreelancerM/manage.py createsuperuser
    ```
    Follow the prompts to create an admin user.

4.  **Run the development server:**
    ```bash
    python FreelancerM/manage.py runserver
    ```

5.  **Access the application:**
    The application should now be accessible at `http://127.0.0.1:8000/`.

## Project Structure

*   `FreelancerM/`: The main Django project directory.
*   `FreelancerM/manage.py`: Django's command-line utility.
*   `requirements.txt`: Python dependencies.
*   `Dockerfile`: Dockerfile for the Django application.
*   `docker-compose.yml`: Docker Compose configuration for development.
