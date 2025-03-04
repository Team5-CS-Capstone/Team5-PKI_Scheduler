# CS-Capstone

A **Vue 3** application built to help class coordinators streamline the scheduling process. Class coordinators can:

1. **Import a CSV schedule** for the semester and automatically detect classes that exceed room capacity.  
2. **Reassign classes** to more suitable rooms, either through basic swaps or a multi-chain process if simple swaps are not feasible.  
3. **Edit class information**, such as enrollment capacity, student enrollment, instructor, time, and section details.  
4. **Export a revised CSV** file reflecting all changes made within the application.

By offering different reassignment strategies and real-time warnings for over-enrolled courses, the application simplifies the coordinator's task of ensuring every class is assigned to a properly sized room.

---
## 🚀 Installation
1️⃣ **Clone the repository:**
```sh
git clone https://github.com/zkak345/Team5-PKI_Scheduler.git
cd Team5-PKI_Scheduler
```

2️⃣ Install dependencies:
```sh
npm install
```

3️⃣ Run application
```sh
npm run dev
```

## Styling with Tailwind CSS
Tailwind CSS is already configured via @tailwindcss/vite.

Simply use Tailwind utility classes in Vue components.

Docs: https://tailwindcss.com/docs/installation/using-vite

## Working with Backend/Database
Everything backend/database related is stored within the ./python_db folder so cd into that folder before anything.
A shared virtual environment exists within this folder that we can easily access using the script below:
```sh
.\flask_venv\Scripts\Activate
```
Once in the venv (flask_env), it should be displayed before your terminal current directory
This virtual environment is required as all needed packages for backend development exist for this project
### app.py - contains all API endpoints and creation of tables for the database


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
