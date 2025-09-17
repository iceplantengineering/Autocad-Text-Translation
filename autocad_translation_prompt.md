# AutoCAD DWG Chinese to Japanese Translation Web Application Development Prompt

## 1. Project Title
**AutoCAD DWG Text Translator (Chinese to Japanese)**

## 2. Project Goal
Develop a web-based application that can automatically extract Chinese text from AutoCAD DWG files (versions 2012 and later), translate it into Japanese, and then re-insert the translated Japanese text back into the DWG file, preserving the original formatting and layout. The application should be deployable on platforms like Netlify.

## 3. Problem Statement
Many engineering and design firms working with international clients or partners frequently encounter AutoCAD DWG files containing text in various languages. Specifically, there is a need to efficiently translate Chinese text within DWG files (from AutoCAD 2012 onwards) into Japanese. Manual translation is time-consuming, error-prone, and does not scale for large projects. Existing solutions often lack the ability to directly process DWG files, handle specific AutoCAD text entities, or seamlessly integrate translation services.

## 4. Target Audience
- Architects, engineers, and designers who receive or produce DWG files with Chinese text and need to work with them in Japanese.  
- Project managers overseeing international design projects requiring multilingual documentation.  
- Companies seeking to automate their translation workflows for CAD drawings.  

## 5. Key Features

### 5.1. DWG File Upload and Processing
- File Upload: Allow users to upload one or more DWG files via a web interface.  
- Version Compatibility: Support DWG files created with AutoCAD 2012 and later versions.  
- Text Extraction: Accurately extract all text entities (e.g. MTEXT, TEXT, ATTRIB, DIMTEXT) from the uploaded DWG files.  
- Encoding Handling: Properly handle various Chinese character encodings within DWG files.  

### 5.2. Chinese to Japanese Translation
- Automated Translation: Integrate with a robust machine translation API (e.g. DeepL, Google Cloud Translation, iFlytek) for high-quality Chinese to Japanese translation.  
- Contextual Translation: Ideally, the translation service should offer some level of contextual understanding to improve accuracy for technical terms.  
- Glossary/Terminology Management (Optional but Recommended): Allow users to upload custom glossaries for specific technical terms to ensure consistent translation.  

### 5.3. Translated Text Re-insertion
- Text Replacement: Replace the original Chinese text entities with their Japanese translations within the DWG file.  
- Formatting Preservation: Maintain original text properties such as font, size, position, layer, and other formatting attributes.  
- Layout Adjustment: Intelligent handling of text length changes after translation to minimize layout disruption. This might involve automatic text wrapping or resizing where appropriate.  

### 5.4. File Download
- Translated DWG Download: Allow users to download the modified DWG file containing the Japanese translations.  
- Translation Report (Optional): Provide a report detailing the extracted Chinese text, its Japanese translation, and any untranslated segments or errors.  

### 5.5. User Interface (UI)
- Intuitive Web Interface: A clean, user-friendly interface for uploading files, initiating translation, and downloading results.  
- Progress Tracking: Display the status of the translation process (e.g. uploading, extracting, translating, re-inserting, complete).  
- Error Handling: Clear error messages and guidance for users in case of issues.  

---

## 6. Technical Requirements

### 6.1. Backend
- **Language**: Python (recommended due to existing libraries for DWG processing and API integrations).  
- **Framework**: Flask or FastAPI for building RESTful APIs.  
- **DWG Processing**:  
  - **Option 1 (Recommended):** Utilize Autodesk Platform Services (APS) Design Automation API for AutoCAD. This ensures compatibility with AutoCAD's internal mechanisms.  
  - **Option 2 (Alternative):** Explore open-source libraries like `ezdxf` (via DXF conversion) or commercial libraries. Direct DWG handling can be complex and risky.  
- **Translation API Integration**: DeepL, Google Cloud Translation, iFlytek.  
- **File Storage**: Temporary storage on AWS S3, Google Cloud Storage, or local.  

### 6.2. Frontend
- **Framework**: React, Vue.js, or Angular.  
- **UI Libraries**: Material-UI, Ant Design, or Bootstrap.  
- **File Upload Component**: e.g. `react-dropzone`.  

### 6.3. Deployment
- **Frontend**: Netlify.  
- **Backend**: Heroku, Google Cloud Run, AWS Lambda, or VPS.  
- **CI/CD**: Automated pipelines for both.  

---

## 7. Development Steps (High-Level)
1. Setup Project Structure.  
2. Autodesk APS Integration.  
3. DWG Text Extraction Module.  
4. Translation Module.  
5. DWG Text Re-insertion Module.  
6. Frontend Development.  
7. Backend API Development.  
8. Error Handling & Logging.  
9. Deployment.  
10. Testing.  

---

## 8. Considerations and Challenges
- DWG Complexity and entity variations.  
- Autodesk APS costs.  
- Translation accuracy and custom glossaries.  
- Layout issues due to text length differences.  
- Performance optimization.  
- Security of uploaded files and API keys.  

---

## 9. Deliverables
- Working web app (Netlify + backend).  
- Source code (frontend & backend).  
- Comprehensive documentation.  
- User guide.  

---

## 10. References
- Autodesk Platform Services (APS) Design Automation API  
- DeepL API Documentation  
- Google Cloud Translation API Documentation  
- ezdxf  
- drawingtotext  
