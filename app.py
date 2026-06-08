from flask import Flask, render_template, request, redirect
import csv
import os
import pytesseract
from PIL import Image
from datetime import datetime
import re
from PIL import ImageOps
import joblib

model = joblib.load(
    "expense_model.pkl"
)

# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

app = Flask(__name__)

CSV_FILE = "expense_data.csv"
UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Store AI prediction results
prediction_result = None
predicted_category = None


@app.route("/")
def home():

    global prediction_result, predicted_category

    data = []
    total = 0

    try:
        with open(CSV_FILE, "r") as file:
            reader = csv.reader(file)
            next(reader)

            for row in reader:
                data.append(row)
                total += float(row[2])

    except:
        pass

    # Grab and clear category prediction after one display
    cat = predicted_category
    predicted_category = None

    return render_template(
        "index.html",
        data=data,
        total=total,
        prediction=prediction_result,
        predicted_category=cat,
    )


@app.route("/add", methods=["POST"])
def add():

    date = request.form["date"]
    category = request.form["category"]
    amount = request.form["amount"]
    note = request.form["note"]

    with open(CSV_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([date, category, amount, note])

    # Regenerate charts
    os.system("python visualize.py > nul 2>&1")

    return redirect("/")


@app.route("/predict_category", methods=["POST"])
def predict_category():

    global predicted_category

    description = request.form["description"]
    predicted_category = model.predict([description])[0]

    return redirect("/")


@app.route("/clear")
def clear():

    global prediction_result, predicted_category

    with open(CSV_FILE, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "Category", "Amount", "Note"])

    # Reset AI results
    prediction_result = None
    predicted_category = None

    # Regenerate empty charts
    os.system("python visualize.py")

    return redirect("/")


@app.route("/ai_recommendation")
def ai_recommendation():

    category_totals = {}

    with open(CSV_FILE, "r") as file:

        reader = csv.reader(file)
        next(reader)

        for row in reader:

            category = row[1]
            amount = float(row[2])

            category_totals[category] = (
                category_totals.get(category, 0)
                + amount
            )

    total = sum(category_totals.values())

    analysis = []
    recommendations = []

    score = 10

    for category, amount in category_totals.items():

        percentage = round(
            amount / total * 100,
            1
        )

        analysis.append({
            "category": category,
            "amount": amount,
            "percentage": percentage
        })

        if category.lower() == "food" and percentage > 40:

            recommendations.append(
                "🍔 Food expenses are very high. Try reducing restaurant spending."
            )

            score -= 2

        elif category.lower() == "shopping" and percentage > 30:

            recommendations.append(
                "🛍 Shopping expenses are increasing. Avoid unnecessary purchases."
            )

            score -= 1

    recommendations.append(
        "💰 Try saving at least 20% of your monthly income."
    )

    return render_template(
        "recommendation.html",
        analysis=analysis,
        recommendations=recommendations,
        total=total,
        score=max(score, 1)
    )


@app.route("/predict_goal", methods=["POST"])
def predict_goal():

    global prediction_result

    goal = request.form["goal"]
    target = float(request.form["target"])
    saving = float(request.form["saving"])

    # Calculate current expenses
    total_expense = 0

    try:
        with open(CSV_FILE, "r") as file:
            reader = csv.reader(file)
            next(reader)

            for row in reader:
                total_expense += float(row[2])

    except:
        pass

    # Simple AI logic
    effective_saving = saving - (total_expense * 0.10)

    if effective_saving <= 0:
        effective_saving = saving

    months = round(target / effective_saving)

    if months <= 12:
        message = "🎉 Goal achievable within 1 year."

    elif months <= 24:
        message = "👍 Goal achievable within 2 years."

    else:
        message = "⚠ Consider increasing your monthly savings."

    prediction_result = {
        "goal": goal,
        "target": int(target),
        "saving": int(saving),
        "months": months,
        "message": message,
    }

    return redirect("/")


@app.route("/scan_receipt", methods=["POST"])
def scan_receipt():

    file = request.files["receipt"]

    if file.filename == "":
        return redirect("/")

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        file.filename
    )

    file.save(filepath)

    image = Image.open(filepath)
    image = ImageOps.grayscale(image)
    image = image.resize(
        (image.width * 3, image.height * 3)
    )
    image = image.point(
        lambda p: 255 if p > 150 else 0
    )

    text = pytesseract.image_to_string(
        image,
        config="--oem 3 --psm 11"
    )

    print("\n===== OCR TEXT =====")
    print(text)
    print("====================")

    text_lower = text.lower()

    # Category Detection
    if any(
        word in text_lower
        for word in [
            "pizza",
            "restaurant",
            "food",
            "foods",
            "dosa",
            "paneer",
            "coffee",
            "cafe",
            "swiggy",
            "zomato"
        ]
    ):
        category = "Food"

    elif any(
        word in text_lower
        for word in [
            "uber",
            "ola",
            "petrol",
            "diesel",
            "bus"
        ]
    ):
        category = "Travel"

    elif any(
        word in text_lower
        for word in [
            "amazon",
            "flipkart",
            "shopping"
        ]
    ):
        category = "Shopping"

    else:
        category = "Others"

    # Extract Final Total
    amount = 0

    keywords = [
        "grand total",
        "amount payable",
        "net amount",
        "total"
    ]

    for key in keywords:

        # Same line: Total 5445.30
        match = re.search(
            rf"{key}\s*[:₹Rs.\s]*([\d,]+\.\d{{2}})",
            text,
            re.IGNORECASE
        )

        if match:

            amount = float(
                match.group(1).replace(",", "")
            )

            break

        # Next line:
        # TOTAL
        # 75.00
        match = re.search(
            rf"{key}\s*\n+\s*([\d,]+\.\d{{2}})",
            text,
            re.IGNORECASE
        )

        if match:

            amount = float(
                match.group(1).replace(",", "")
            )

            break

    print("FINAL TOTAL =", amount)

    with open(CSV_FILE, "a", newline="") as file:

        writer = csv.writer(file)

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d"),
            category,
            amount,
            "AI Receipt Scan"
        ])

    os.system("python visualize.py")

    return redirect("/")


if not os.path.exists(CSV_FILE):

    with open(CSV_FILE, "w", newline="") as file:

        writer = csv.writer(file)

        writer.writerow([
            "Date",
            "Category",
            "Amount",
            "Note"
        ])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)