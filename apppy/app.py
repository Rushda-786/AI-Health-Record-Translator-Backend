from flask import Flask, request, jsonify
from flask_cors import CORS
from pypdf import PdfReader
import re

app = Flask(__name__)
CORS(app)


# ==========================================
# HOME ROUTE
# ==========================================

@app.route("/")
def home():
    return jsonify({
        "message": "Welcome to AI Health Record Translator Backend!"
    })


# ==========================================
# HELPER FUNCTION
# ==========================================

def analyze_lab_value(
    test_name,
    value,
    unit,
    normal_min,
    normal_max,
    reference
):

    if value < normal_min:
        status = "Low"
    elif value > normal_max:
        status = "High"
    else:
        status = "Normal"


    # ======================================
    # HEMOGLOBIN
    # ======================================

    if test_name == "Hemoglobin":

        if status == "Low":

            explanation = (
                f"Hemoglobin is {value} {unit}, which is below "
                f"the displayed reference range of {reference}. "
                "Low hemoglobin can be associated with anemia, "
                "but a healthcare professional should interpret "
                "the result in context."
            )

            suggestion = (
                "Discuss the result with a healthcare professional. "
                "They may consider diet, iron status and other tests "
                "depending on the person's overall condition."
            )

        elif status == "High":

            explanation = (
                f"Hemoglobin is {value} {unit}, which is above "
                f"the displayed reference range of {reference}."
            )

            suggestion = (
                "Discuss the result with a healthcare professional "
                "if it remains elevated or if symptoms are present."
            )

        else:

            explanation = (
                f"Hemoglobin is {value} {unit}, which is within "
                f"the displayed reference range of {reference}."
            )

            suggestion = (
                "Continue a balanced diet and follow routine "
                "health checkups as recommended by a healthcare professional."
            )


    # ======================================
    # GLUCOSE
    # ======================================

    elif test_name == "Glucose":

        if status == "Low":

            explanation = (
                f"Glucose is {value} {unit}, which is below "
                f"the displayed reference range of {reference}."
            )

            suggestion = (
                "Low glucose can have different causes. "
                "Discuss the result with a healthcare professional, "
                "especially if symptoms such as dizziness, sweating "
                "or weakness occur."
            )

        elif status == "High":

            explanation = (
                f"Glucose is {value} {unit}, which is above "
                f"the displayed fasting reference range of {reference}."
            )

            suggestion = (
                "Discuss the result with a healthcare professional. "
                "They may recommend repeat testing or additional tests "
                "depending on the clinical situation."
            )

        else:

            explanation = (
                f"Glucose is {value} {unit}, which is within "
                f"the displayed fasting reference range of {reference}."
            )

            suggestion = (
                "Maintain balanced meals, regular physical activity "
                "and routine health monitoring."
            )


    # ======================================
    # VITAMIN B12
    # ======================================

    elif test_name == "Vitamin B12":

        if status == "Low":

            explanation = (
                f"Vitamin B12 is {value} {unit}, which is below "
                f"the displayed reference range of {reference}."
            )

            suggestion = (
                "Discuss the result with a healthcare professional. "
                "Foods containing vitamin B12 may include eggs, dairy "
                "products, fish, meat and fortified foods."
            )

        elif status == "High":

            explanation = (
                f"Vitamin B12 is {value} {unit}, which is above "
                f"the displayed reference range of {reference}."
            )

            suggestion = (
                "Discuss a persistently high result with a healthcare "
                "professional, particularly if vitamin supplements are being used."
            )

        else:

            explanation = (
                f"Vitamin B12 is {value} {unit}, which is within "
                f"the displayed reference range of {reference}."
            )

            suggestion = (
                "Maintain a balanced diet containing appropriate "
                "sources of vitamin B12."
            )


    # ======================================
    # VITAMIN D
    # ======================================

    elif test_name == "Vitamin D":

        if status == "Low":

            explanation = (
                f"Vitamin D is {value} {unit}, which is below "
                f"the displayed reference range of {reference}."
            )

            suggestion = (
                "Discuss the result with a healthcare professional. "
                "They can advise whether dietary changes, sunlight exposure "
                "or supplementation is appropriate."
            )

        elif status == "High":

            explanation = (
                f"Vitamin D is {value} {unit}, which is above "
                f"the displayed reference range of {reference}."
            )

            suggestion = (
                "Discuss a high result with a healthcare professional, "
                "especially if vitamin D supplements are being used."
            )

        else:

            explanation = (
                f"Vitamin D is {value} {unit}, which is within "
                f"the displayed reference range of {reference}."
            )

            suggestion = (
                "Maintain a balanced diet and follow healthy lifestyle habits."
            )


    else:

        explanation = (
            f"{test_name} is {value} {unit}. "
            f"The displayed reference range is {reference}."
        )

        suggestion = (
            "Discuss the result with a healthcare professional "
            "if you have concerns."
        )


    return {
        "test": test_name,
        "name": test_name,
        "value": value,
        "unit": unit,
        "reference": reference,
        "status": status,
        "explanation": explanation,
        "suggestion": suggestion
    }


# ==========================================
# UPLOAD AND ANALYZE MEDICAL REPORT
# ==========================================

@app.route("/upload", methods=["POST"])
def upload_file():

    # ======================================
    # CHECK FILE
    # ======================================

    if "file" not in request.files:

        return jsonify({
            "error": "No file uploaded."
        }), 400


    file = request.files["file"]


    if file.filename == "":

        return jsonify({
            "error": "No file selected."
        }), 400


    try:

        # ==================================
        # READ PDF
        # ==================================

        reader = PdfReader(file)

        extracted_text = ""


        for page in reader.pages:

            text = page.extract_text()

            if text:
                extracted_text += text + "\n"


        if not extracted_text.strip():

            return jsonify({
                "error": "Could not extract readable text from this PDF."
            }), 400


        text_lower = extracted_text.lower()


        # ==================================
        # FINDINGS DETECTION
        # ==================================

        findings = []


        finding_keywords = {

            "itching": "Itching",

            "redness": "Skin redness",

            "fever": "Fever",

            "open wounds": "Open wounds",

            "dermatitis": "Possible dermatitis",

            "skin irritation": "Skin irritation",

            "rash": "Skin rash",

            "swelling": "Swelling",

            "pain": "Pain",

            "dry skin": "Dry skin"

        }


        for keyword, result in finding_keywords.items():

            if keyword in text_lower:

                if result not in findings:
                    findings.append(result)


        # ==================================
        # LAB RESULTS
        # ==================================

        lab_results = []

        explanations = []

        suggestions = []


        # ==================================
        # HEMOGLOBIN
        # ==================================

        hemoglobin_match = re.search(
            r"hemoglobin\s*[:\-]?\s*(\d+(?:\.\d+)?)",
            text_lower
        )


        if hemoglobin_match:

            value = float(
                hemoglobin_match.group(1)
            )


            result = analyze_lab_value(
                "Hemoglobin",
                value,
                "g/dL",
                12,
                15,
                "12.0 - 15.0 g/dL"
            )


            lab_results.append(result)

            explanations.append(
                result["explanation"]
            )

            suggestions.append(
                result["suggestion"]
            )


        # ==================================
        # GLUCOSE
        # ==================================

        glucose_match = re.search(
            r"(?:fasting blood glucose|glucose)\s*[:\-]?\s*(\d+(?:\.\d+)?)",
            text_lower
        )


        if glucose_match:

            value = float(
                glucose_match.group(1)
            )


            result = analyze_lab_value(
                "Glucose",
                value,
                "mg/dL",
                70,
                99,
                "70 - 99 mg/dL"
            )


            lab_results.append(result)

            explanations.append(
                result["explanation"]
            )

            suggestions.append(
                result["suggestion"]
            )


        # ==================================
        # VITAMIN B12
        # ==================================

        b12_match = re.search(
            r"(?:vitamin\s*b12|b12)\s*[:\-]?\s*(\d+(?:\.\d+)?)",
            text_lower
        )


        if b12_match:

            value = float(
                b12_match.group(1)
            )


            result = analyze_lab_value(
                "Vitamin B12",
                value,
                "pg/mL",
                200,
                900,
                "200 - 900 pg/mL"
            )


            lab_results.append(result)

            explanations.append(
                result["explanation"]
            )

            suggestions.append(
                result["suggestion"]
            )


        # ==================================
        # VITAMIN D
        # ==================================

        vitamin_d_match = re.search(
            r"(?:vitamin\s*d3|vitamin\s*d)\s*[:\-]?\s*(\d+(?:\.\d+)?)",
            text_lower
        )


        if vitamin_d_match:

            value = float(
                vitamin_d_match.group(1)
            )


            result = analyze_lab_value(
                "Vitamin D",
                value,
                "ng/mL",
                30,
                100,
                "30 - 100 ng/mL"
            )


            lab_results.append(result)

            explanations.append(
                result["explanation"]
            )

            suggestions.append(
                result["suggestion"]
            )


        # ==================================
        # ABNORMAL VALUES
        # ==================================

        abnormal_values = []


        for lab in lab_results:

            if lab["status"] != "Normal":

                abnormal_values.append({

                    "test": lab["test"],

                    "value": lab["value"],

                    "unit": lab["unit"],

                    "status": lab["status"],

                    "reference": lab["reference"]

                })


        # ==================================
        # OVERALL SUMMARY
        # ==================================

        if (
            len(abnormal_values) == 0
            and len(findings) == 0
        ):

            overall_summary = (
                "The uploaded report was analyzed successfully. "
                "No abnormal laboratory values or listed clinical findings "
                "were detected by this demo system."
            )


        elif len(abnormal_values) > 0:

            abnormal_names = ", ".join(
                item["test"]
                for item in abnormal_values
            )


            overall_summary = (
                "The report contains some values that are outside "
                "the displayed reference ranges. The values requiring "
                f"attention include: {abnormal_names}. "
                "These results should be interpreted together with "
                "the person's symptoms and medical history by a healthcare professional."
            )


        else:

            overall_summary = (
                "The report contains some clinical findings that were "
                "detected by the system. These findings are not a diagnosis "
                "and should be interpreted by a healthcare professional."
            )


        # ==================================
        # GENERAL HEALTH ADVICE
        # ==================================

        general_advice = [

            "Maintain a balanced diet containing a variety of nutritious foods.",

            "Drink adequate water and maintain regular daily activity.",

            "Follow the advice provided by your healthcare professional.",

            "Do not start or stop medication or supplements based only on this tool.",

            "If symptoms are persistent, severe or getting worse, seek medical attention."

        ]


        # ==================================
        # DOCTOR ADVICE
        # ==================================

        doctor_advice = (
            "Consider discussing abnormal results or persistent symptoms "
            "with a qualified healthcare professional. Seek prompt medical "
            "attention for severe or rapidly worsening symptoms."
        )


        # ==================================
        # RETURN RESULT TO REACT
        # ==================================

        return jsonify({

            "message":
                "Medical report analyzed successfully!",

            "filename":
                file.filename,

            "text":
                extracted_text,

            "findings":
                findings,

            "lab_results":
                lab_results,

            "explanations":
                explanations,

            "suggestions":
                suggestions,

            "abnormal_values":
                abnormal_values,

            "overall_summary":
                overall_summary,

            "general_advice":
                general_advice,

            "doctor_advice":
                doctor_advice

        })


    except Exception as e:

        return jsonify({

            "error":
                f"Error processing PDF: {str(e)}"

        }), 500


# ==========================================
# START FLASK SERVER
# ==========================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )