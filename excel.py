import pandas as pd

def read_excel(file_path):
    excel_data = pd.read_excel(file_path)


    # Remove "email" from columns
    columns = excel_data.columns.tolist()
    if "Email" in columns:
        columns.remove("Email")
    if "email" in columns:
        columns.remove("email")
    columns = [word.lower() for word in columns]

    # Check if "name" is in the columns and add "surname" if it's present
    if "name" in columns and "surname" not in columns:
        columns.append("surname")

    data = pd.DataFrame(excel_data)
    data = data.rename(columns=str.lower)

    print("Successfully read Excel file.")
    return data, columns

