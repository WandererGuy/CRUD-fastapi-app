# usage tutorial 
Configuration Summary
Your .env file now includes: ✅ PostgreSQL - Connects to localhost:5432 (matches docker-compose)
✅ JWT Settings - 30-minute access tokens, 7-day refresh tokens
✅ Redis - Connects to localhost:6379 (matches docker-compose)
Next Steps to Run the Application
Start Docker services:
```
docker-compose up -d
```
Generate and update JWT_SECRET_KEY in .env file
Install Python dependencies:
```
pip install -r requirements.txt
```
Run database migrations:
```
alembic upgrade head
```
Start the FastAPI application:
```
python app.py 
```
Your API will be available at http://localhost:8000 with interactive docs at http://localhost:8000/docs








# basic CRUD application using alembic , postgresql (docker), fastapi 
usage:
CRUD brand into postgres database 


# how to run 
- create  .env file put in root folder , similar variable like in .env.example file
- activate postgres database
```
docker compose up -d
```

- create a conda environment , activate it 
```
pip install -r requirements.txt
```

- create brand table in postgres database 
```
alembic upgrade head 
```

- seed database with fake data 
```
python seed.py
```
- run app
```
python app.py
```

- then go to http://127.0.0.1:8000/docs to try those juicy APIs


# teach alembic 
## create alembic 
### in project root 
alembic init alembic


### load .env file for alembic/env.py

### Open alembic/env.py, and make sure your models’ metadata is imported:
```
from myapp.models import Base  # adjust path to where your models are
target_metadata = Base.metadata
```
### alembic 
```
alembic revision --autogenerate -m "create users table"
```

### finally
```
alembic upgrade head 
```




# project structure 
API -> service -> repository -> DB postgres (in docker)

using alembic to handle changes in models code


# Seeding the Database

To populate the database with example brand data:

```bash
python seed.py
```

This will:
- Clear existing brand data (comment out `clear_brands()` in seed.py if you want to keep existing data)
- Add 11 example brands (10 active, 1 inactive)
- Display the seeded brands in the console

The seeder includes brands like Apple, Nike, Samsung, Google, Microsoft, etc. 


