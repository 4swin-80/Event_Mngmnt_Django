# Event Cue Automation Project

Event Cue Automation is a Django-based event management system that helps admins manage events, bookings, operators, and live cue alerts. The project also includes a cue engine that monitors scheduled cues and sends alerts to the assigned operator, backup operators, and the event admin when needed.

## Main Features

- Event creation and management
- Customer booking flow
- Operator assignment for cues
- Automated cue monitoring
- Backup escalation for missed cues
- Live notifications using Django Channels and Redis
- Attendance and supporting event operations

## Project Structure

The repository root contains the virtual environment and supporting files.

The main Django project is inside:

`eventmanage/`

Important files:

- `eventmanage/manage.py`
- `eventmanage/eventmanage/settings.py`
- `eventmanage/core/management/commands/run_cue_engine.py`
- `eventmanage/core/management/commands/startall.py`

## Requirements

Before running the project, make sure you have:

- Python installed
- Redis installed and running
- A virtual environment created

## Quick Start

If Redis is already running, you can start the full project from the `eventmanage` folder with:

```cmd
python manage.py startall
```

This runs both the Django development server and the cue engine together.

## Installation

### 1. Clone the repository

```cmd
git clone <repository-url>
cd Event_Cue_Automation_project
```

### 2. Create a virtual environment

```cmd
python -m venv venv
```

### 3. Activate the virtual environment

On Windows:

```cmd
venv\Scripts\activate
```

On Linux or macOS:

```sh
source venv/bin/activate
```

### 4. Install dependencies

```cmd
pip install -r requirements.txt
```

### 5. Go to the Django project folder

```cmd
cd eventmanage
```

## Environment Variables

A local `.env` file is already included inside the `eventmanage/` folder for development.

Path:

`eventmanage/.env`

Current values:

```env
SECRET_KEY=your-secret-key
DEBUG=True
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
```

If needed, you can edit that file and change the values for your system.

## Database Setup

The project is configured to use SQLite by default.

Run migrations before starting the app:

```cmd
python manage.py migrate
```

If you want to create an admin account:

```cmd
python manage.py createsuperuser
```

## Running Redis

Redis must be running before starting the project.

On Windows, if you downloaded Redis as a zip package, open the extracted folder and run:

```cmd
redis-server.exe
```

On Linux or macOS, you can usually run:

```sh
redis-server
```

## Running the Project

There are two ways to start the application.

### Option 1: Start everything with one command

This command starts both the Django development server and the cue engine:

```cmd
python manage.py startall
```

### Option 2: Start services manually

Start the Django server:

```cmd
python manage.py runserver
```

In a separate terminal, start the cue engine:

```cmd
python manage.py run_cue_engine
```

The cue engine checks pending cues continuously and processes alerts automatically.

## Notes

- Redis is required for live notifications because the project uses Django Channels with Redis channel layers.
- The cue engine should be kept running while testing or using scheduled cue alerts.
- SQLite is used as the default database in the current configuration.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
