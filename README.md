# Installation Guide

## Step 1 — Install Python

Python is the programming language this application runs on. You need to install it once before anything else.

1. Go to the official Python download page:
   👉 https://www.python.org/downloads/release/python-3123/
2. Scroll down to the **Files** section and download the installer for your operating system:
   - **Windows**: Choose `Windows installer (64-bit)`
   - **macOS**: Choose `macOS 64-bit universal2 installer`
3. Run the downloaded installer.
   - ⚠️ **Windows users**: On the first screen of the installer, make sure to check the box that says **"Add Python to PATH"** before clicking *Install Now*. This is an easy step to miss!
4. Follow the on-screen instructions to complete the installation.

> The application was developed and tested with **Python 3.12.3**, but any newer version of Python should work as well.

---

## Step 2 — Download the Project

You need to get the project files onto your computer. There are two ways to do this:

**Option A — Download as ZIP (recommended if you don't know what Git is):**
1. Go to the project page on GitHub.
2. Click the green **`<> Code`** button near the top right.
3. Select **"Download ZIP"**.
4. Once downloaded, right-click the ZIP file and select **"Extract All"** (Windows) or double-click it (macOS) to unpack the files.
5. Remember where you saved the extracted folder — you'll need it in the next steps.

**Option B — Clone with Git (if you have Git installed):**
```
git clone <project-url>
```
Replace `<project-url>` with the link shown on the project page.

---

## Step 3 — Add the Annotation Data

You should have received the annotation data as an **email attachment**. 

1. Download the attached annotation file(s) from the email.
2. Copy or move them into the **project folder** you just downloaded — the same folder that contains the files `label_app.py` and `assigenment_r2_r.pkl`.

---

## Step 4 — Open a Terminal and Navigate to the Project Folder

A terminal (also called a command line or command prompt) lets you type commands directly to your computer. Here's how to open one and get to the right folder:

**Windows:**
1. Press `Win + R`, type `cmd`, and press Enter. A black window will appear — that's the terminal.
2. Type the following command and press Enter, replacing the path with the actual location of your project folder:
   ```
   cd C:\Users\YourName\Downloads\project-folder-name
   ```
   > **Tip:** You can find the full path by navigating to the folder in File Explorer, clicking the address bar at the top, and copying the text that appears.

**macOS:**
1. Open **Spotlight** with `Cmd + Space`, type `Terminal`, and press Enter.
2. Type the following and press Enter, replacing the path with the actual location:
   ```
   cd /Users/YourName/Downloads/project-folder-name
   ```
   > **Tip:** You can drag and drop the folder directly into the Terminal window after typing `cd ` (with a space) to automatically fill in the path.

**How to verify you're in the right folder:**
Type `ls` (macOS) or `dir` (Windows) and press Enter. You should see `label_app.py` listed among the files.

---

## Step 5 — Install the Required Packages

The application depends on a few additional components that need to be installed. Still in your terminal from the previous step, run the following command and press Enter:

```
pip install -r requirements.txt
```

This may take a minute or two. You'll see text scrolling by — that's normal! Wait until it finishes and the cursor returns to a new line. If you see an error mentioning `pip` is not found, try `pip3` instead:

```
pip3 install -r requirements.txt
```

---

## Step 6 — Run the Application

You're almost there! In the same terminal window, run:

```
python label_app.py
```

After a moment, you'll see a message in the terminal containing a link that looks something like this:

```
Running on http://127.0.0.1:5000
```

**Copy that link and paste it into any web browser** (Chrome, Firefox, Safari, Edge — any of them work). The application will open right in your browser.

Happy annotating! 🎉

---

## Troubleshooting

| Problem | What to try |
|---|---|
| `python` not recognized | Try `python3` instead of `python` |
| `pip` not recognized | Try `pip3` instead of `pip` |
| "Module not found" error | Make sure you ran Step 5 successfully |
| Page doesn't load in browser | Double-check you copied the full link from the terminal, including `http://` |
| Still stuck? | Take a screenshot of the error message and send it to the project maintainer |