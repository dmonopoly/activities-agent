"""Google Sheets tool - MCP-style tool for saving activities to Google Sheets"""

import os
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Google Sheets API scope
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# File to store credentials
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"


def _get_credentials():
    """Get valid user credentials from storage or prompt for authorization"""
    creds = None

    # Check if token file exists
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    "credentials.json not found. Please download it from Google Cloud Console "
                    "and place it in the backend directory."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials for next run
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return creds


def save_to_sheets(
    activities: list[dict[str, Any]], spreadsheet_id: str | None = None
) -> dict[str, Any]:
    """
    Save activities to a Google Sheet

    Args:
        activities: List of activity dictionaries
        spreadsheet_id: Optional existing spreadsheet ID. If not provided, creates a new sheet.

    Returns:
        Dictionary with spreadsheet_id and spreadsheet_url
    """
    try:
        creds = _get_credentials()
        service = build("sheets", "v4", credentials=creds)

        if not spreadsheet_id:
            # Create a new spreadsheet
            spreadsheet = {"properties": {"title": "Activity Ideas"}}
            spreadsheet = (
                service.spreadsheets()
                .create(body=spreadsheet, fields="spreadsheetId")
                .execute()
            )
            spreadsheet_id = spreadsheet.get("spreadsheetId")

        # Prepare data
        values = [
            [
                "Name",
                "Location",
                "Description",
                "Price",
                "Opening Hours",
                "Category",
                "URL",
            ]
        ]

        for activity in activities:
            opening_hours = activity.get("opening_hours", "")
            values.append(
                [
                    activity.get("name", ""),
                    activity.get("location", ""),
                    activity.get("description", ""),
                    activity.get("price", ""),
                    opening_hours,
                    activity.get("category", ""),
                    activity.get("url", ""),
                ]
            )

        # Write to sheet
        range_name = "Sheet1!A1"
        body = {"values": values}

        result = (
            service.spreadsheets()
            .values()
            .update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="RAW",
                body=body,
            )
            .execute()
        )

        spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"

        return {
            "spreadsheet_id": spreadsheet_id,
            "spreadsheet_url": spreadsheet_url,
            "rows_updated": result.get("updatedCells", 0),
        }

    except HttpError as error:
        return {
            "error": f"An error occurred: {error}",
            "spreadsheet_id": None,
            "spreadsheet_url": None,
        }
    except FileNotFoundError as error:
        return {"error": str(error), "spreadsheet_id": None, "spreadsheet_url": None}


# Tool definition for LLM function calling
TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "save_to_sheets",
        "description": "Save a list of activities to a Google Sheet. Creates a new sheet if spreadsheet_id is not provided.",
        "parameters": {
            "type": "object",
            "properties": {
                "activities": {
                    "type": "array",
                    "description": "List of activity objects to save",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "location": {"type": "string"},
                            "description": {"type": "string"},
                            "price": {"type": "string"},
                            "opening_hours": {
                                "type": "string",
                                "description": "Opening hours or event time",
                            },
                            "category": {"type": "string"},
                            "url": {"type": "string"},
                        },
                    },
                },
                "spreadsheet_id": {
                    "type": "string",
                    "description": "Optional existing Google Sheet ID. If not provided, creates a new sheet.",
                },
            },
            "required": ["activities"],
        },
    },
}
