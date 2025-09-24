import sys, os; sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import pytest
from rules_engine import matches_condition, rule_matches

def sample_email():
    return {"id":"abc","sender":"news@newsletter.example","to_field":"me@example.com",
            "subject":"Monthly Update","snippet":"Here is your monthly update",
            "internal_date":1600000000,"is_read":False}

def test_contains():
    assert matches_condition(sample_email(), {"field":"From","predicate":"contains","value":"newsletter"})

def test_equals_subject():
    assert matches_condition(sample_email(), {"field":"Subject","predicate":"equals","value":"Monthly Update"})

def test_rule_all_predicate():
    rule={"conditionsPredicate":"All","conditions":[{"field":"From","predicate":"contains","value":"newsletter"},{"field":"Subject","predicate":"contains","value":"Update"}]}
    assert rule_matches(sample_email(),rule)

def test_rule_any_predicate():
    rule={"conditionsPredicate":"Any","conditions":[{"field":"From","predicate":"contains","value":"nobody"},{"field":"Subject","predicate":"contains","value":"Update"}]}
    assert rule_matches(sample_email(),rule)
