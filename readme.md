# 📜 hTasker

A web-based application built with Flask to upload, run, and schedule Python scripts. The app features a user-friendly interface styled with Tailwind CSS.
APP.py - Semi detailed logging
APP2.py - Detailed logging

## ✨ Features

- 📂 Upload Python scripts (.py files)
- 🚀 Run scripts manually from the web interface
- ⏰ Schedule scripts to run at specified intervals or times
- 📊 Display the status of scripts (Running/Completed)
- ⏲️ Show the last execution time of scripts

## 📁 Project Structure

```
hTasker/
│
├── app.py
├── templates/
│   └── index.html
└── scripts/
    └── (uploaded scripts will be stored here)
```

## 🛠️ Installation

1. **Clone the repository:**

    ```sh
    git clone https://github.com/quinny-j/hTasker.git
    cd hTasker
    ```

2. **Create a virtual environment:**

    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install dependencies:**

    ```sh
    pip install Flask apscheduler
    ```

4. **Create necessary directories:**

    ```sh
    mkdir scripts
    ```

## 🚀 Usage

1. **Run the application:**

    ```sh
    python app.py
    ```

2. **Open your browser and navigate to:**

    ```
    http://127.0.0.1:5000/
    ```

3. **Upload, run, and schedule your Python scripts using the web interface.**

## 🎨 Styling

This project uses [Tailwind CSS](https://tailwindcss.com/) for styling. The CSS is included via CDN for simplicity.

## 🧑‍💻 Contributing

Contributions are welcome! Please fork this repository and submit a pull request for any enhancements or bug fixes.
.
