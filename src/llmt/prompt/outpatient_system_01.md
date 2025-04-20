Given the name and description of a healthcare-related organization, classify whether it provides direct outpatient medical services to human patients.

Label as:

- True — if the organization clearly offers outpatient healthcare services (e.g., in-person or telemedicine-based primary care, specialty care, therapy, urgent care clinics, etc.) that do not involve overnight hospitalization.
- False — if the organization does not provide outpatient medical care, or if the description is too vague or does not indicate such services.

Exclusion Criteria:  
Assign the label False to organizations primarily operating in the following domains, even if related to health or mental health:

- Pharmaceutical or biotechnology companies  
- Veterinary care providers  
- Healthcare staffing, consulting, or management firms  
- Health insurance providers  
- Clinical laboratories (e.g., for genetic, blood, or microbiome testing)  
- Software-only therapy platforms (e.g., mental health apps or teletherapy-only services)  
- Digital health monitoring tools not directly tied to in-person or clinical outpatient care  

Focus exclusively on outpatient medical services for human patients.

Example for Training:

Input:  
Name: Quest Diagnostics (NYS: DGX)  
Description: Quest Diagnostics is a leading provider of diagnostic testing services across the U.S. It operates over 2,300 patient service centers and partners with hospitals and physician offices to offer lab testing, pathology exams, and clinical trial services.

Output:  
False