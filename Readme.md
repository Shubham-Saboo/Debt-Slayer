# Debt Slayer: AI Debt Management Advisor

Debt Slayer is an AI-powered debt management advisor designed to help users create a consolidated debt report and develop a personalized debt management strategy. By analyzing the user's financial profile, Debt Slayer provides actionable insights and a tailored repayment plan. The application leverages a Retrieval-Augmented Generation (RAG) pipeline powered by the Deepseek R1 reasoning model, to offer users the most relevant and effective debt management strategies.

---

Tech Stack: MongoDB, Retrieval Augmented Generation, Deepseek R1 reasoning model, Streamlit

### DEMO VIDEO: https://youtu.be/q4Nu5Xq1qJs

[![Watch the video](https://img.youtube.com/vi/q4Nu5Xq1qJs/0.jpg)](https://www.youtube.com/watch?v=q4Nu5Xq1qJs)





## Table of Contents
1. [Environment Setup](#environment-setup)
    - [Using Conda](#using-conda)
    - [Using Pip](#using-pip)
2. [Running the Project](#running-the-project)

---

## Environment Setup

### Using Conda
Conda is an open-source package management system and environment management system.

1. Create a new conda environment:
    ```
    conda create -n myenv python=3.9
    ```

2. Activate the environment:
    ```
    conda activate myenv
    ```

3. Install dependencies from `requirements.txt` (if available):
    ```
    pip install -r requirements.txt
    ```

---

### Using Pip
Pip is the standard package installer for Python.

1. Install virtualenv if you don't have it:
    ```
    pip install virtualenv
    ```

2. Create a virtual environment:
    ```
    virtualenv venv
    ```

3. Activate the virtual environment:
    - On Windows:
        ```
        venv\Scripts\activate
        ```
    - On macOS/Linux:
        ```
        source venv/bin/activate
        ```

4. Install dependencies from `requirements.txt` (if available):
    ```
    pip install -r requirements.txt
    ```

---

## Running the Project
    ```
    streamlit run frontend.py
    ```

Ensure that all dependencies are installed before running the scripts.

---

If you encounter any issues, feel free to reach out or check the documentation for the tools mentioned above.
