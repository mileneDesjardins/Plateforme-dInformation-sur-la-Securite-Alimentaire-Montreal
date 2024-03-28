from datetime import datetime

from database import Database
from notification import send_courriel


# def detect_new_contraventions_and_notify(session):
#     try:
#         db = Database.get_db()
#
#         # Retrieve the last check date for new contraventions
#         last_check_date = session.get("last_check_date")
#
#         # If it's the first check, use an earlier date to get all contraventions
#         if last_check_date is None:
#             last_check_date = datetime.min
#
#         # Retrieve all contraventions added since the last check
#         new_contraventions = db.get_contraventions_between(
#             last_check_date, datetime.now())
#
#         # Update the last check date
#         session["last_check_date"] = datetime.now()
#
#         # If new contraventions have been detected, send an email
#         if new_contraventions:
#             destinataire = 'destinataire@example.com'  # Replace with the recipient's email address
#             send_courriel(destinataire, new_contraventions)
#
#         return new_contraventions
#     except Exception as e:
#         # Log the error or handle it appropriately
#         print(f"An error occurred: {e}")
#         return []
