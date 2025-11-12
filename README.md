#### **Al-based-Generative-design-of-Hydropower-plants**

### 🧩 **Problem Description**

The proposed system focuses on **AI-based Generative Design of Hydropower Plants**, integrating **civil structures**, **hydro-mechanical**, and **electro-mechanical equipment** into an automated design workflow.

The core idea is to leverage **Blender software** in combination with **Python programming** to create **intelligent, parameter-driven 3D models** of hydropower plant components.

Users can provide inputs either through **keyboard entry** or via a **voice assistant interface** powered by **OpenAI Whisper**. These inputs — such as dimensions, capacity requirements, or site-specific constraints — are processed to dynamically generate or adapt **pre-loaded templates** within Blender.

The result is a **customized 3D model** that meets client requirements with high accuracy and efficiency.

By automating the generative design process, this project:

* Eliminates repetitive manual modeling
* Accelerates the design cycle
* Reduces human error
* Enables AI-driven optimization (for performance, sustainability, and cost-effectiveness)

Ultimately, this system serves as a **smart design assistant for hydropower engineers and planners**, enabling **rapid prototyping and visualization** of hydropower infrastructure.

## 🏗️ **System Overview**

A Python-based Blender automation framework that dynamically generates 3D models for hydropower components such as:

* **Generator**
* **Turbine**
* **Intake Structure**

### 📂 **Repository Structure**

```
AI-Generative-HydroDesign/
│
├── ui_app.py                 # Front-end (Tkinter + ttkbootstrap)
├── hydro_master.py           # Blender 3D generation logic
├── requirements.txt          # Python dependencies
├── sample_config.json        # Example input configuration
└── assets/                   # Screenshots, figures, and output models
```

## 🧱 **Features**

| Feature                         | Description                                     |
| ------------------------------- | ----------------------------------------------- |
| **Dynamic Parameterization**    | Adjust geometries based on user inputs          |
| **Automated Blender Control**   | Generates `.blend` files automatically          |
| **3D Animation**                | Rotating shafts, moving gates, and crane motion |
| **Material & Lighting Effects** | Adds realistic colors and environment lighting  |
| **Error Handling**              | Validates user inputs and config generation     |
| **Custom Export Paths**         | Saves generated models in user-selected folders |

## ⚙️ **Installation**

### 1️⃣ Prerequisites

* **Windows 10/11** (Recommended)
* **Python 3.10+**
* **Blender 4.5 or higher**
* **pip** package manager

### 2️⃣ Clone the Repository

```bash
git clone https://github.com/<your-username>/AI-Generative-HydroDesign.git
cd AI-Generative-HydroDesign
```

### 3️⃣ Install Required Packages

```bash
pip install -r requirements.txt
```

or manually:

```bash
pip install ttkbootstrap
```

---

### 4️⃣ Verify Blender Path

Ensure this line in `ui_app.py` matches your system’s Blender path:

```python
blender_path = r"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"
```

If Blender is installed elsewhere, modify accordingly.


## 🚀 **Running the Project**

### 🧭 Step 1: Launch UI

```bash
python ui_app.py
```

### 🧮 Step 2: Select Component

Choose from:

* ⚡ Generator
* 🌪 Turbine
* 🌊 Intake Structure

### 🧱 Step 3: Enter Parameters

Input geometry, dimensions, and mechanical specifications.

### 📁 Step 4: Choose Export Folder

Select where `.blend` files will be saved.

### 🧰 Step 5: Click **“Generate Model”**

* Blender opens in background mode
* 3D model generated and animated
* Output saved in your selected folder


## 📘 **Example Configuration File**

```json
{
  "component": "generator",
  "values": {
    "stator_radius": 5.0,
    "stator_height": 3.0,
    "rotor_radius": 3.0,
    "rotor_height": 2.0,
    "shaft_radius": 0.5,
    "shaft_height": 8.0,
    "base_radius": 7.0,
    "base_height": 1.0
  },
  "export_folder": "C:\\Users\\YourName\\Desktop\\Exports"
}
```

---

## 🧩 **Output Examples**

* `generator.blend` → Animated stator, rotor, and shaft
* `turbine.blend` → Spiral casing with vanes and rotating blades
* `intake_structure.blend` → Multi-bay intake with gates, crane, and tunnels

## 🧠 **Architecture**

```
[User Interface] --> [JSON Config Generator] --> [Blender Engine]
          ↑                    ↓
    [Voice Input / Keyboard]   |
          └────> [AI Processing Module]
```

## ⚒️ **Troubleshooting**

| Issue                 | Cause                         | Solution                         |
| --------------------- | ----------------------------- | -------------------------------- |
| ❌ Config file error   | JSON not generated or missing | Ensure export folder is writable |
| ⚠️ Empty model        | Invalid or zero input values  | Verify parameter values in app   |
| ❌ Blender not found   | Wrong installation path       | Correct Blender path in code     |
| ⚙️ UI freezes briefly | Blender background processing | Wait until the process completes |


## 🧾 **requirements.txt**

```
ttkbootstrap==1.10.1
```


## 🖼️ **Screenshots**

(Place your screenshots inside `/assets` and link below.)

* **Figure 1:** Generator UI Interface – *[Insert Screenshot of Generator UI Here]*
* **Figure 2:** Turbine Configuration Window – *[Insert Screenshot of Turbine UI Here]*
* **Figure 3:** Generated 3D Model in Blender – *[Insert Screenshot of Model Output Here]*

---

## 🧭 **Future Enhancements**

* 🔊 Voice-command integration using **OpenAI Whisper**
* 🤖 AI-based optimization and design recommendations
* 🌐 Export to **WebGL / glTF** for browser visualization
* 🧮 CFD-based performance validation

---

## 📚 **References**

1. Blender API Documentation — [https://docs.blender.org/api/current/](https://docs.blender.org/api/current/)
2. Python Tkinter Docs — [https://docs.python.org/3/library/tkinter.html](https://docs.python.org/3/library/tkinter.html)
3. ttkbootstrap UI Framework — [https://ttkbootstrap.readthedocs.io/](https://ttkbootstrap.readthedocs.io/)
4. OpenAI Whisper — [https://github.com/openai/whisper](https://github.com/openai/whisper)
5. IEEE Hydropower Standards — IEEE Std 1010-2006

---

## 🧑‍💻 **Author**

**Aashrith Kiran**
Department of Computer Science & Engineering
7th Semester Capstone Project
📘 Title: *AI-Based Generative Design of Hydropower Plants*
© 2025 – All rights reserved.

**Harsha P**
Department of Computer Science & Engineering
7th Semester Capstone Project
📘 Title: *AI-Based Generative Design of Hydropower Plants*
© 2025 – All rights reserved.

**Narayana A**
Department of Computer Science & Engineering
7th Semester Capstone Project
📘 Title: *AI-Based Generative Design of Hydropower Plants*
© 2025 – All rights reserved.
