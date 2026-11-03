
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from analyzer import analyze_expenses
from statement_importer import import_gpay_pdf
import io
import pandas as pd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "Smart Expense Analyzer API is running"}


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    filename = (file.filename or "").lower()
    contents = await file.read()

    try:
        if filename.endswith(".pdf"):
            df = import_gpay_pdf(io.BytesIO(contents))

            if df.empty:
                raise HTTPException(
                    status_code=400,
                    detail="No transactions could be extracted from this PDF."
                )

            # Keep expenses only; received money is income, not spending.
            df = df[df["Type"] == "Expense"].copy()

            if df.empty:
                raise HTTPException(
                    status_code=400,
                    detail="No expense transactions were found in this PDF."
                )

            # Basic category assignment; refine these rules later.
            
            def categorize(description):
                """
                Categorize a transaction based on recognizable merchant keywords.
                Unknown personal UPI names are categorized as Personal Payments.
                """

                if not description:
                    return "Personal Payments"

                text = str(description).lower().strip()

                categories = {
                    "Food & Dining": [
                        "hotel shivaprasad",
                        "pabbas",
                        "ideal cafe",
                        "cafe",
                        "restaurant",
                        "hotel",
                        "food",
                        "swiggy",
                        "zomato",
                        "blinkit",
                        "zepto",
                        "bigbasket",
                        "dmart",
                        "grocery",
                        "supermarket",
                        "bakery",
                        "juice",
                        "tea",
                        "coffee",
                    ],

                    "Subscriptions": [
                        "spotify",
                        "netflix",
                        "youtube premium",
                        "hotstar",
                        "prime video",
                        "amazon prime",
                        "bookmyshow",
                        "pvr",
                        "inox",
                    ],

                    "Transport": [
                        "uber",
                        "ola",
                        "rapido",
                        "irctc",
                        "redbus",
                        "fastag",
                        "petrol",
                        "fuel",
                        "diesel",
                        "parking",
                        "bus",
                        "train",
                        "taxi",
                        "auto",
                    ],

                    "Shopping": [
                        "amazon",
                        "flipkart",
                        "myntra",
                        "ajio",
                        "meesho",
                        "nykaa",
                        "reliance retail",
                        "shopping",
                        "fashion",
                        "clothing",
                    ],

                    "Bills & Recharge": [
                        "airtel",
                        "jio",
                        "bsnl",
                        "vi recharge",
                        "recharge",
                        "electricity",
                        "broadband",
                        "internet bill",
                        "water bill",
                        "gas bill",
                        "mobile bill",
                    ],

                    "Health & Personal Care": [
                        "pharmacy",
                        "medplus",
                        "apollo pharmacy",
                        "hospital",
                        "clinic",
                        "doctor",
                        "medicine",
                        "medical",
                        "salon",
                        "beauty parlour",
                    ],

                    "Education": [
                        "college",
                        "university",
                        "school",
                        "tuition",
                        "udemy",
                        "coursera",
                        "books",
                        "stationery",
                    ],

                    "Travel": [
                        "hotel booking",
                        "airline",
                        "flight",
                        "indigo",
                        "air india",
                        "goibibo",
                        "oyo",
                        "accommodation",
                    ],
                }

                # Match recognizable merchant names first
                for category, keywords in categories.items():
                    if any(keyword in text for keyword in keywords):
                        return category

                # Fallback for individual names or unclear UPI descriptions
                return "Personal Payments"


            df["Category"] = df["Description"].apply(categorize)
            csv_data = df[["Date", "Category", "Amount"]].to_csv(index=False)
            result = analyze_expenses(io.BytesIO(csv_data.encode("utf-8")))

        elif filename.endswith(".csv"):
            result = analyze_expenses(io.BytesIO(contents))

        else:
            raise HTTPException(
                status_code=400,
                detail="Please upload a CSV or PDF file."
            )

        return result

    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=f"Could not analyze this file: {str(error)}"
        )
