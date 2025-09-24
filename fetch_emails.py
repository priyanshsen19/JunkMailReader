import argparse
from auth import get_gmail_service
from db import init_db, upsert_email
from utils import parse_internal_date, header_value

def fetch_messages(service, max_results=100, sender=None):
    query = ""
    if sender:
        query = f"from:{sender}"
    results = service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
    return results.get("messages", [])

def fetch_and_store(max_results=100, sender=None):
    service = get_gmail_service()
    conn = init_db()
    msgs = fetch_messages(service, max_results=max_results, sender=sender)
    print(f"Found {len(msgs)} messages.")

    for m in msgs:
        msg = service.users().messages().get(userId="me", id=m["id"], format="full").execute()
        headers = msg.get("payload", {}).get("headers", [])
        sender_val = header_value(headers, "From")
        to_field = header_value(headers, "To")
        subject = header_value(headers, "Subject")
        snippet = msg.get("snippet", "")
        internal_date = parse_internal_date(msg.get("internalDate", "0"))
        labels = msg.get("labelIds", [])
        is_read = "UNREAD" not in labels

        email = {
            "id": msg["id"],
            "sender": sender_val,
            "to_field": to_field,
            "subject": subject,
            "snippet": snippet,
            "internal_date": internal_date,
            "is_read": is_read,
            "labels": labels
        }
        upsert_email(conn, email)

    print("Done storing messages.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--max", type=int, default=100)
    parser.add_argument("--from", dest="from_sender", type=str, help="Filter by sender email")
    args = parser.parse_args()
    fetch_and_store(max_results=args.max, sender=args.from_sender)
