<h1 align="center">🧠 Smart Task Analyzer</h1>

<p align="center">
  AI-powered intelligent task scoring & prioritization system.<br/>
  Built with <b>Django REST Framework</b> + <b>Modern Frontend UI</b>.
</p>

<p align="center">
  <img src="images/ui-home.png" width="70%"/>
  <img src="https://img.shields.io/badge/Status-Production%20Ready-success?style=for-the-badge"/>
</p>

---

## 📌 Overview

Smart Task Analyzer is a full-stack intelligent system that evaluates, ranks, and recommends tasks based on:

- **Urgency** (deadline-based)
- **Importance**
- **Effort**
- **Dependencies**
- **Weighted strategies** (Smart / Deadline-first / Impact-based)

Ideal for:
✔ Internship assignments  
✔ Productivity tools  
✔ AI-based prioritization systems  
✔ Portfolio projects  

---

## 🖼️ Demo UI

### 🔹 Home Screen
![Home UI](images/ui-home.png)

### 🔹 Scored Task Results
![Scored Tasks](images/ui-results.png)

### 🔹 Top 3 Suggestions
![Top 3](images/ui-top3.png)

---

## 🎥 Live Demo

<p align="center">
  <img src="demo.gif" width="800px">
</p>

--

## ✨ Features

### 🧠 Intelligent Scoring Algorithm  
A custom decision engine that calculates a score for each task based on:
- Time sensitivity
- Importance level
- Required effort
- Dependency impact

### 🥇 Suggest Top 3 Tasks  
Recommends the best tasks to do *right now* based on strategy.

### 🎨 Modern Frontend  
- Responsive UI  
- Smooth layout  
- Strategy dropdown  
- Bulk JSON task input  
- Clean task cards  

### 🔗 REST API  
| Endpoint | Method | Description |
|---------|--------|-------------|
| `/api/tasks/analyze/` | POST | Score and sort tasks |
| `/api/tasks/suggest/` | GET | Top 3 recommended tasks |

---

## 🛠️ Tech Stack

### **Backend**
- Django 5.2
- Django REST Framework
- django-cors-headers
- Python 3.x

### **Frontend**
- HTML5  
- CSS3 (Custom UI)  
- JavaScript  

---

## 📁 Folder Structure
task-analyzer/
│
├── backend/
│ ├── manage.py
│ ├── task_analyzer/
│ └── tasks/
│ ├── models.py
│ ├── views.py
│ ├── serializers.py
│ ├── urls.py
│
├── frontend/
│ ├── index.html
│ ├── style.css
│ └── script.js
│
├── images/
│ ├── ui-home.png
│ ├── ui-results.png
│ └── ui-top3.png
│
└── README.md

---

## 👨‍🎓 Author

**Keerthivasan Boopathy**  
Francis Xavier Engineering College  
Smart Task Analyzer — Internship Assignment  



