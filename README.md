# CS-Capstone

A **Vue 3** application built to help class coordinators streamline the scheduling process. Class coordinators can:

1. **Import a CSV schedule** for the semester and automatically detect classes that exceed room capacity.  
2. **Reassign classes** to more suitable rooms, either through basic swaps or a multi-chain process if simple swaps are not feasible.  
3. **Edit class information**, such as enrollment capacity, student enrollment, instructor, time, and section details.  
4. **Export a revised CSV** file reflecting all changes made within the application.

By offering different reassignment strategies and real-time warnings for over-enrolled courses, the application simplifies the coordinator's task of ensuring every class is assigned to a properly sized room.

---
## 🚀 Start Application
1. **Clone the repository:**
```sh
git clone https://github.com/zkak345/Team5-PKI_Scheduler.git
cd Team5-PKI_Scheduler
```

2. Install dependencies and frontend testing framework:
```sh
cd frontend
npm install
npm install --save-dev jest @vue/test-utils vue-jest@next babel-jest @babel/preset-env
```

3. Create and Activate Virtual Environment and Install Requirements
```sh
cd python-db
python -m venv <name_of_env>
.\flask_venv\Scripts\Activate
pip install -r requirements.txt
```

4. Populate database:
```sh
python import_csv_to_table.py 
```

5. Run backend (flask)
```sh
python app.py
```

6. Run application
```sh
cd ..
cd frontend
npm run dev
```


## Styling with Tailwind CSS
Tailwind CSS is already configured via @tailwindcss/vite.

Simply use Tailwind utility classes in Vue components.

Docs: https://tailwindcss.com/docs/installation/using-vite

## Working with Backend
Everything backend/database related is stored within the ./python_db folder so cd into that folder before anything.
A shared virtual environment exists within this folder that we can easily access using the script below:
```sh
.\flask_venv\Scripts\Activate
```
Once in the venv (flask_env), it should be displayed before your terminal current directory
This virtual environment is required as all needed packages for backend development exist for this project

### Run Flask API (app.py)
```sh
python app.py
```
It will run on **http://127.0.0.1:5000** and endpoints for the API will be located within app.py \
Example of an endpoint that takes in a parameter for class ID below:

## API Endpoints
| **Endpoint**       | **Method** | **Description**                       |
|--------------------|-----------|---------------------------------------|
| `/classes`        | `GET`      | Fetch all class details               |
| `/class/<id>`     | `GET`      | Fetch a single class by ID            |
| `/class/<id>/update-enrollment` | `PUT` | Fetch a single class by ID and update its enrollment accordingly|
| `/upload`     | `PUT`      | Receives and handles CSV importing to the database |
| `/export`     | `PUT`      | Exports classes from the database into a CSV |
| `/class/<id>/professors`     | `GET`      | Retrieves the profs associated with a specific class |
| `/class/<id>/possible-reassignments`     | `GET`      | Retrieves the possible class swaps for a specific class |
| `/swap_classes`     | `PUT`     | Swaps classes (enrollment, max enroll, and possibly time)|


## SQLite Database Installation/Recommendations 
Install [SQLite](https://www.sqlite.org/download.html) here, steps below:
- Click the link and download the precompiled binaries for windows (sqlite-tools-win-x64-3490100.zip)
- Create and put the download into a folder at root level **C:\sqlite**
- Extract the download file into this folder
- Edit your environmental variables, specifically PATH (click, edit, new) and add **C:\sqlite**
- Restart env and possibly computer
To enter the SQLite terminal run:
```sh
sqlite3 database.db
```
Then regular SQL syntax can be used to run commands on the db e.g. (select * from <table_name>) \
SQLite viewer extension for VS Code is also very useful (allows you to open .db files in SQLite form)

## Branching Strategy
Our branching strategy is very simple: each user has their branch which they push to, and when they are ready to share their changes to others they make a pull request with their changes, pushing the contents into the dev branch. When the dev branch has significant progress, typically when the group meets we merge all of the contents from dev into main (the master branch of this application).

## Release Notes
#### Milestone #1:
- The design idea was completed in Figma
- These design ideas were implemented into our application user interface
- Implemented a working and finalized navigation system for the application
- Set up the codebase (vue.js app) including tailwind implementation and SQLite database implementation was started
- CSV file parsing implemented and working properly (within python-db\interaction.py)
- The CSV files themselves are stored within the top level of  the my-vue-app folder.
- Re-usable component implemented for the sidebar navigation
- The implementation of a basic algorithm was unable to be implemented this algorithm as we first will need a connection between our frontend/backend which will be the focus of our next milestone


#### Milestone #2:
- Backend --> Front-end connection made through app.py
-   API endpoint created for classes
-   API endpoint created for class details, and for updating enrollment
-   API endpoint created for upload
-   API endpoint created for classes
-   API endpoint created for export
-   File picker for upload created, uses previous workflow to populate database
-   Search feature for classes page implemented
-   Some minor documentation created
-   Overshot on github actions as tests haven't been created just yet


#### Milestone #3:
- Reformatting of the Crosslist section
- CSV file cleaning feature, and removal of trailing lines
- Dynamic generation of a course cross list dictionary
- Feature to combine all cross listed classes as one entry
- Documentation Pages for front and backend
- Tests set up and ready to start unit tests
- Color feature implented to indicate if current enrollment is above maximum


#### Milestone #4:
- Issue with enrollment in crosslisted classes fixed
- New database linking professor IDs and class IDs
  - Classes can have multiple professors (TAs) and multiple professors can teach multiple classes
- API endpoint to call professor(s) from class ID
- Professor(s) for class now displayed on the class details page
- Filter by classes with enrollment past maximum first
- Dropdown menu to select amount of students in class
- **Very** basic algorithm implemented for determining sufficient class locations
- Menu to select a class to swap with
- API endpoint to swap necessary class information

#### Milestone #5:
- Algorithm finished to check for different time slot swaps
- Algorithm results implemented into the UI, with the ability to swap
- Exporting to CSV is fixed to work with changes in the database
- Swap API endpoint changed to work for all uses in the application
- Filter classes button moved to top of UI for cleaner UX
- Logging is done on all class swaps into a text file for class coordinators to view if needed
- Back button added in the class details page for each class for cleaner UI/UX
- Testing is being added now, and after the video is posted
