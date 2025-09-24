import json, time
from db import init_db, fetch_all_emails
from auth import get_gmail_service

# to load the rules from json
def load_rules(path="rules.json"):
    with open(path, "r") as f:
        return json.load(f)

#to filter data based on the rule
def matches_condition(email, cond):
    field = cond.get("field")
    predicate = cond.get("predicate", "").lower()
    value = cond.get("value")
    field_map = {
        "from": email.get("sender", ""), "to": email.get("to_field", ""),
        "subject": email.get("subject", ""), "message": email.get("snippet", ""),
        "received": email.get("internal_date")
    }
    actual = field_map.get(field.lower())
    if actual is None: 
        return False

    if predicate == "contains":
        return str(value).lower() in str(actual).lower()
    if predicate == "does not contain":
        return str(value).lower() not in str(actual).lower()
    if predicate == "equals":
        return str(actual).lower() == str(value).lower()
    if predicate == "does not equal":
        return str(actual).lower() != str(value).lower()
    return False

# fetch all the emails with matching rule
def rule_matches(email, rule):
    conds = rule.get("conditions", [])
    pred = rule.get("conditionsPredicate", "All").lower()
    results = [matches_condition(email, c) for c in conds]
    return all(results) if pred == "all" else any(results)

# to fetch the label id
def ensure_label(service, label_name):
    labels = service.users().labels().list(userId="me").execute().get("labels", [])
    for l in labels:
        if l.get("name") == label_name:
            return l.get("id")
    body = {"name": label_name, "labelListVisibility": "labelShow", "messageListVisibility": "show"}
    created = service.users().labels().create(userId="me", body=body).execute()
    return created.get("id")

# to apply action of the rule
def apply_action(service, email_id, action):
    t = action.get("type")
    if t == "mark_as_read":
        service.users().messages().modify(userId="me", id=email_id, body={"removeLabelIds": ["UNREAD"]}).execute()
        print(f"✔ Email {email_id} marked as READ")
    elif t == "mark_as_unread":
        service.users().messages().modify(userId="me", id=email_id, body={"addLabelIds": ["UNREAD"]}).execute()
        print(f"✔ Email {email_id} marked as UNREAD")
    elif t == "move_to_label":
        label = action.get("label")
        if not label: 
            print(f"⚠ Skipped: move_to_label action missing 'label'")
            return
        label_id = ensure_label(service, label)
        service.users().messages().modify(
            userId="me", id=email_id,
            body={"addLabelIds": [label_id], "removeLabelIds": ["INBOX"]}
        ).execute()
        print(f"✔ Email {email_id} moved to label '{label}'")
    else:
        print(f"⚠ Unknown action type: {t}")

# rule engine service
def apply_rules(path="rules.json"):
    rules = load_rules(path).get("rules", [])
    service = get_gmail_service()
    conn = init_db()
    emails = fetch_all_emails(conn)

    for email in emails:
        matched = False
        for rule in rules:
            if rule_matches(email, rule):
                matched = True
                print(f"\n📧 Email {email['id']} from '{email.get('sender')}' matched a rule")
                for action in rule.get("actions", []):
                    apply_action(service, email["id"], action)
        if not matched:
            print(f"— Email {email['id']} did not match any rule")

if __name__ == "__main__":
    apply_rules()
