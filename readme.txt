--> How To Run Event Cue Automation Project : 


STEP 1 : From Extracted redis zip folder, doubleclick 'redis-server.exe' and run it in background.

STEP 2 : cmd --> activate venv --> cd eventmanage --> python manage.py startall


--> How To Run Event Cue Automation Project(from Github) : 


1. Clone the repository

git clone <repository-url>
cd eventmanage


2. Create virtual environment

python -m venv venv


3. Activate virtual environment

Windows:
venv\Scripts\activate

Linux/Mac:
source venv/bin/activate


4. Install dependencies

pip install -r requirements.txt


5.Download Redis And Run Redis server

redis-server


6. Start Django server and run_cue_engine

cd eventmanage --> python manage.py startall