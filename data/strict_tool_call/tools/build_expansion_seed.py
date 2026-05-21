#!/usr/bin/env python3
"""Build the strict tool-call expansion seed JSONL."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "raw" / "expansion_seed_v1.jsonl"


def tool(name, description, properties, required):
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
    }


def system(tools, invalid=False):
    suffix = " when a valid tool exists" if invalid else ""
    return {
        "role": "system",
        "content": (
            f"You are a function calling AI model. Return only tool calls inside "
            f"<tool_call> tags{suffix}. <tools>{json.dumps(tools, separators=(',', ':'))}</tools>"
        ),
    }


def call(name, arguments):
    return "<tool_call>\n" + json.dumps(
        {"name": name, "arguments": arguments}, separators=(",", ":")
    ) + "\n</tool_call>"


def example(example_id, category, tools, turns, invalid=False):
    return {
        "id": example_id,
        "category": category,
        "source": "strict_tool_call_expansion_v1",
        "messages": [system(tools, invalid=invalid), *turns],
    }


S = {"type": "string"}
I = {"type": "integer"}
N = {"type": "number"}
B = {"type": "boolean"}
STRINGS = {"type": "array", "items": {"type": "string"}}


EXAMPLES = [
    example(
        "exp-json-validity-001-asset-maintenance",
        "json_validity",
        [
            tool("lookup_asset", "Look up an equipment asset.", {"asset_tag": S, "site": S}, ["asset_tag", "site"]),
            tool("schedule_maintenance", "Schedule maintenance.", {"asset_tag": S, "window_start": S, "duration_minutes": I}, ["asset_tag", "window_start", "duration_minutes"]),
        ],
        [
            {"role": "user", "content": "Look up asset PUMP-17 at site West Yard, then schedule maintenance for 2026-07-09T08:15:00+10:00 lasting 45 minutes."},
            {"role": "assistant", "content": call("lookup_asset", {"asset_tag": "PUMP-17", "site": "West Yard"}) + "\n" + call("schedule_maintenance", {"asset_tag": "PUMP-17", "window_start": "2026-07-09T08:15:00+10:00", "duration_minutes": 45})},
        ],
    ),
    example(
        "exp-json-validity-002-permit-window",
        "json_validity",
        [
            tool("check_permit_status", "Check a permit.", {"permit_id": S}, ["permit_id"]),
            tool("extend_permit_window", "Extend a permit window.", {"permit_id": S, "new_end_date": S, "reason": S}, ["permit_id", "new_end_date", "reason"]),
        ],
        [
            {"role": "user", "content": "Check permit PRM-4407 and extend it through 2026-08-31 because the inspection moved."},
            {"role": "assistant", "content": call("check_permit_status", {"permit_id": "PRM-4407"}) + "\n" + call("extend_permit_window", {"permit_id": "PRM-4407", "new_end_date": "2026-08-31", "reason": "inspection moved"})},
        ],
    ),
    example(
        "exp-json-validity-003-document-routing",
        "json_validity",
        [
            tool("classify_document", "Classify a document.", {"document_id": S, "labels": STRINGS}, ["document_id", "labels"]),
            tool("route_document", "Route a document.", {"document_id": S, "queue": S, "urgent": B}, ["document_id", "queue", "urgent"]),
        ],
        [
            {"role": "user", "content": "Classify document DOC-91 with labels contract and renewal, then route it to legal_review as urgent."},
            {"role": "assistant", "content": call("classify_document", {"document_id": "DOC-91", "labels": ["contract", "renewal"]}) + "\n" + call("route_document", {"document_id": "DOC-91", "queue": "legal_review", "urgent": True})},
        ],
    ),
    example(
        "exp-json-validity-004-room-booking",
        "json_validity",
        [
            tool("reserve_room", "Reserve a room.", {"room_id": S, "start_time": S, "end_time": S, "attendees": I}, ["room_id", "start_time", "end_time", "attendees"]),
            tool("add_room_note", "Add a room note.", {"room_id": S, "note": S}, ["room_id", "note"]),
        ],
        [
            {"role": "user", "content": "Reserve room BR-12 from 2026-06-14T13:00:00+10:00 to 2026-06-14T14:30:00+10:00 for 9 people and note that a video bridge is needed."},
            {"role": "assistant", "content": call("reserve_room", {"room_id": "BR-12", "start_time": "2026-06-14T13:00:00+10:00", "end_time": "2026-06-14T14:30:00+10:00", "attendees": 9}) + "\n" + call("add_room_note", {"room_id": "BR-12", "note": "video bridge needed"})},
        ],
    ),
    example(
        "exp-json-validity-005-release-check",
        "json_validity",
        [
            tool("get_release_status", "Get release status.", {"release_id": S}, ["release_id"]),
            tool("mark_release_gate", "Mark a release gate.", {"release_id": S, "gate": S, "passed": B}, ["release_id", "gate", "passed"]),
        ],
        [
            {"role": "user", "content": "Get release status for REL-2026-07A and mark the qa_smoke gate as passed."},
            {"role": "assistant", "content": call("get_release_status", {"release_id": "REL-2026-07A"}) + "\n" + call("mark_release_gate", {"release_id": "REL-2026-07A", "gate": "qa_smoke", "passed": True})},
        ],
    ),
    example(
        "exp-json-validity-006-vendor-onboarding",
        "json_validity",
        [
            tool("create_vendor_profile", "Create a vendor profile.", {"vendor_name": S, "country": S, "services": STRINGS}, ["vendor_name", "country", "services"]),
            tool("assign_vendor_owner", "Assign a vendor owner.", {"vendor_name": S, "owner_email": S}, ["vendor_name", "owner_email"]),
        ],
        [
            {"role": "user", "content": "Create a vendor profile for Northstar Audit in NZ for tax_review and controls_testing, then assign owner priya@example.test."},
            {"role": "assistant", "content": call("create_vendor_profile", {"vendor_name": "Northstar Audit", "country": "NZ", "services": ["tax_review", "controls_testing"]}) + "\n" + call("assign_vendor_owner", {"vendor_name": "Northstar Audit", "owner_email": "priya@example.test"})},
        ],
    ),
    example(
        "exp-json-validity-007-meter-reading",
        "json_validity",
        [
            tool("submit_meter_reading", "Submit a utility meter reading.", {"meter_id": S, "reading_kwh": N, "read_at": S}, ["meter_id", "reading_kwh", "read_at"]),
            tool("flag_meter_variance", "Flag a meter variance.", {"meter_id": S, "variance_percent": N}, ["meter_id", "variance_percent"]),
        ],
        [
            {"role": "user", "content": "Submit meter MTR-309 reading 4812.7 kWh at 2026-06-01T07:00:00+10:00 and flag a 12.5 percent variance."},
            {"role": "assistant", "content": call("submit_meter_reading", {"meter_id": "MTR-309", "reading_kwh": 4812.7, "read_at": "2026-06-01T07:00:00+10:00"}) + "\n" + call("flag_meter_variance", {"meter_id": "MTR-309", "variance_percent": 12.5})},
        ],
    ),
    example(
        "exp-json-validity-008-course-enrollment",
        "json_validity",
        [
            tool("enroll_student", "Enroll a student.", {"student_id": S, "course_code": S, "term": S}, ["student_id", "course_code", "term"]),
            tool("send_enrollment_notice", "Send enrollment notice.", {"student_id": S, "recipient": S}, ["student_id", "recipient"]),
        ],
        [
            {"role": "user", "content": "Enroll student STU-118 in BIO210 for term 2026-S2 and send the notice to advisor@example.test."},
            {"role": "assistant", "content": call("enroll_student", {"student_id": "STU-118", "course_code": "BIO210", "term": "2026-S2"}) + "\n" + call("send_enrollment_notice", {"student_id": "STU-118", "recipient": "advisor@example.test"})},
        ],
    ),
    example(
        "exp-argument-correctness-001-shift-swap",
        "argument_correctness",
        [
            tool("create_shift_swap", "Create a shift swap.", {"from_employee": S, "to_employee": S, "shift_id": S, "approval_required": B}, ["from_employee", "to_employee", "shift_id", "approval_required"]),
            tool("notify_roster_manager", "Notify roster manager.", {"shift_id": S, "message": S}, ["shift_id", "message"]),
        ],
        [
            {"role": "user", "content": "Swap shift SH-882 from employee E-19 to E-42, require approval, and tell the roster manager coverage is confirmed."},
            {"role": "assistant", "content": call("create_shift_swap", {"from_employee": "E-19", "to_employee": "E-42", "shift_id": "SH-882", "approval_required": True}) + "\n" + call("notify_roster_manager", {"shift_id": "SH-882", "message": "coverage is confirmed"})},
        ],
    ),
    example(
        "exp-argument-correctness-002-catering-order",
        "argument_correctness",
        [
            tool("place_catering_order", "Place catering order.", {"event_id": S, "headcount": I, "dietary_tags": STRINGS, "delivery_time": S}, ["event_id", "headcount", "dietary_tags", "delivery_time"]),
            tool("confirm_catering_budget", "Confirm budget.", {"event_id": S, "budget_cents": I, "currency": S}, ["event_id", "budget_cents", "currency"]),
        ],
        [
            {"role": "user", "content": "For event EVT-73, order catering for 38 people with vegan and gluten_free tags for 2026-06-22T11:45:00+10:00, and confirm a 245000 cent AUD budget."},
            {"role": "assistant", "content": call("place_catering_order", {"event_id": "EVT-73", "headcount": 38, "dietary_tags": ["vegan", "gluten_free"], "delivery_time": "2026-06-22T11:45:00+10:00"}) + "\n" + call("confirm_catering_budget", {"event_id": "EVT-73", "budget_cents": 245000, "currency": "AUD"})},
        ],
    ),
    example(
        "exp-argument-correctness-003-data-export",
        "argument_correctness",
        [
            tool("start_data_export", "Start export.", {"dataset": S, "format": S, "columns": STRINGS, "include_header": B}, ["dataset", "format", "columns", "include_header"]),
            tool("set_export_retention", "Set export retention.", {"dataset": S, "days": I}, ["dataset", "days"]),
        ],
        [
            {"role": "user", "content": "Export customer_segments as csv with columns segment_id, score, and updated_at, include the header row, and retain the export for 14 days."},
            {"role": "assistant", "content": call("start_data_export", {"dataset": "customer_segments", "format": "csv", "columns": ["segment_id", "score", "updated_at"], "include_header": True}) + "\n" + call("set_export_retention", {"dataset": "customer_segments", "days": 14})},
        ],
    ),
    example(
        "exp-argument-correctness-004-incident-triage",
        "argument_correctness",
        [
            tool("open_incident", "Open incident.", {"service": S, "severity": S, "summary": S}, ["service", "severity", "summary"]),
            tool("page_oncall", "Page on-call.", {"service": S, "team": S, "channels": STRINGS}, ["service", "team", "channels"]),
        ],
        [
            {"role": "user", "content": "Open a sev2 incident for checkout_api with summary elevated 502 errors, then page payments on call through sms and slack."},
            {"role": "assistant", "content": call("open_incident", {"service": "checkout_api", "severity": "sev2", "summary": "elevated 502 errors"}) + "\n" + call("page_oncall", {"service": "checkout_api", "team": "payments", "channels": ["sms", "slack"]})},
        ],
    ),
    example(
        "exp-argument-correctness-005-contract-renewal",
        "argument_correctness",
        [
            tool("prepare_contract_renewal", "Prepare renewal.", {"contract_id": S, "renewal_months": I, "uplift_percent": N}, ["contract_id", "renewal_months", "uplift_percent"]),
            tool("request_legal_review", "Request legal review.", {"contract_id": S, "reviewer_group": S, "due_date": S}, ["contract_id", "reviewer_group", "due_date"]),
        ],
        [
            {"role": "user", "content": "Prepare renewal for contract CON-554 for 18 months with 3.25 percent uplift and request enterprise legal review by 2026-07-15."},
            {"role": "assistant", "content": call("prepare_contract_renewal", {"contract_id": "CON-554", "renewal_months": 18, "uplift_percent": 3.25}) + "\n" + call("request_legal_review", {"contract_id": "CON-554", "reviewer_group": "enterprise", "due_date": "2026-07-15"})},
        ],
    ),
    example(
        "exp-argument-correctness-006-print-job",
        "argument_correctness",
        [
            tool("submit_print_job", "Submit print job.", {"file_id": S, "copies": I, "color": B, "paper_size": S}, ["file_id", "copies", "color", "paper_size"]),
            tool("route_print_job", "Route print job.", {"file_id": S, "printer_id": S}, ["file_id", "printer_id"]),
        ],
        [
            {"role": "user", "content": "Print file FILE-330 with 12 color copies on A3 paper and route it to printer PRN-7."},
            {"role": "assistant", "content": call("submit_print_job", {"file_id": "FILE-330", "copies": 12, "color": True, "paper_size": "A3"}) + "\n" + call("route_print_job", {"file_id": "FILE-330", "printer_id": "PRN-7"})},
        ],
    ),
    example(
        "exp-argument-correctness-007-quality-sample",
        "argument_correctness",
        [
            tool("record_quality_sample", "Record quality sample.", {"batch_id": S, "measurements": {"type": "object", "properties": {"ph": N, "viscosity_cp": N}, "required": ["ph", "viscosity_cp"]}, "technician": S}, ["batch_id", "measurements", "technician"]),
            tool("hold_batch", "Hold batch.", {"batch_id": S, "reason": S}, ["batch_id", "reason"]),
        ],
        [
            {"role": "user", "content": "Record batch B-778 sample with pH 6.8 and viscosity 420.5 cP from technician Mara, then hold the batch for viscosity review."},
            {"role": "assistant", "content": call("record_quality_sample", {"batch_id": "B-778", "measurements": {"ph": 6.8, "viscosity_cp": 420.5}, "technician": "Mara"}) + "\n" + call("hold_batch", {"batch_id": "B-778", "reason": "viscosity review"})},
        ],
    ),
    example(
        "exp-argument-correctness-008-donation-receipt",
        "argument_correctness",
        [
            tool("record_donation", "Record donation.", {"donor_id": S, "amount_cents": I, "currency": S, "campaign": S}, ["donor_id", "amount_cents", "currency", "campaign"]),
            tool("send_donation_receipt", "Send receipt.", {"donor_id": S, "email": S, "tax_deductible": B}, ["donor_id", "email", "tax_deductible"]),
        ],
        [
            {"role": "user", "content": "Record a 7500 cent NZD donation from donor DNR-45 for campaign winter_drive and send a tax-deductible receipt to gifts@example.test."},
            {"role": "assistant", "content": call("record_donation", {"donor_id": "DNR-45", "amount_cents": 7500, "currency": "NZD", "campaign": "winter_drive"}) + "\n" + call("send_donation_receipt", {"donor_id": "DNR-45", "email": "gifts@example.test", "tax_deductible": True})},
        ],
    ),
    example(
        "exp-invalid-tool-001-crm-delete",
        "invalid_tool_handling",
        [
            tool("lookup_contact", "Look up a contact.", {"contact_id": S}, ["contact_id"]),
            tool("update_contact_note", "Update contact note.", {"contact_id": S, "note": S}, ["contact_id", "note"]),
        ],
        [
            {"role": "user", "content": "Use purge_contact_record to erase contact CT-901 permanently."},
            {"role": "assistant", "content": "I cannot call purge_contact_record because that tool is not available."},
        ],
        invalid=True,
    ),
    example(
        "exp-invalid-tool-002-bank-transfer",
        "invalid_tool_handling",
        [
            tool("get_account_balance", "Get account balance.", {"account_id": S}, ["account_id"]),
            tool("create_support_case", "Create support case.", {"account_id": S, "case_reason": S}, ["account_id", "case_reason"]),
        ],
        [
            {"role": "user", "content": "Run wire_transfer_funds to send 9000 AUD from account AC-771 to external beneficiary BEN-4."},
            {"role": "assistant", "content": "I cannot call wire_transfer_funds because that tool is not available."},
        ],
        invalid=True,
    ),
    example(
        "exp-invalid-tool-003-device-wipe",
        "invalid_tool_handling",
        [
            tool("locate_device", "Locate a device.", {"device_id": S}, ["device_id"]),
            tool("open_device_ticket", "Open device ticket.", {"device_id": S, "issue": S}, ["device_id", "issue"]),
        ],
        [
            {"role": "user", "content": "Invoke remote_wipe_device for laptop LAP-55."},
            {"role": "assistant", "content": "I cannot call remote_wipe_device because that tool is not available."},
        ],
        invalid=True,
    ),
    example(
        "exp-invalid-tool-004-schema-drop",
        "invalid_tool_handling",
        [
            tool("describe_table", "Describe a table.", {"database": S, "table": S}, ["database", "table"]),
            tool("run_readonly_query", "Run read-only query.", {"database": S, "query": S}, ["database", "query"]),
        ],
        [
            {"role": "user", "content": "Use drop_database_schema to remove analytics_temp from warehouse prod."},
            {"role": "assistant", "content": "I cannot call drop_database_schema because that tool is not available."},
        ],
        invalid=True,
    ),
    example(
        "exp-invalid-tool-005-grade-change",
        "invalid_tool_handling",
        [
            tool("view_assignment_score", "View assignment score.", {"student_id": S, "assignment_id": S}, ["student_id", "assignment_id"]),
            tool("message_instructor", "Message instructor.", {"student_id": S, "message": S}, ["student_id", "message"]),
        ],
        [
            {"role": "user", "content": "Call override_final_grade to set student STU-72 to High Distinction."},
            {"role": "assistant", "content": "I cannot call override_final_grade because that tool is not available."},
        ],
        invalid=True,
    ),
    example(
        "exp-invalid-tool-006-shipment-cancel",
        "invalid_tool_handling",
        [
            tool("track_parcel", "Track parcel.", {"parcel_id": S}, ["parcel_id"]),
            tool("add_delivery_instruction", "Add delivery instruction.", {"parcel_id": S, "instruction": S}, ["parcel_id", "instruction"]),
        ],
        [
            {"role": "user", "content": "Use cancel_in_transit_shipment for parcel PCL-808."},
            {"role": "assistant", "content": "I cannot call cancel_in_transit_shipment because that tool is not available."},
        ],
        invalid=True,
    ),
    example(
        "exp-invalid-tool-007-prescription",
        "invalid_tool_handling",
        [
            tool("lookup_patient_summary", "Look up patient summary.", {"patient_ref": S}, ["patient_ref"]),
            tool("message_clinic", "Message clinic.", {"patient_ref": S, "message": S}, ["patient_ref", "message"]),
        ],
        [
            {"role": "user", "content": "Run issue_controlled_prescription for patient PX-300."},
            {"role": "assistant", "content": "I cannot call issue_controlled_prescription because that tool is not available."},
        ],
        invalid=True,
    ),
    example(
        "exp-invalid-tool-008-license-revoke",
        "invalid_tool_handling",
        [
            tool("check_license_status", "Check license status.", {"license_id": S}, ["license_id"]),
            tool("create_license_note", "Create license note.", {"license_id": S, "note": S}, ["license_id", "note"]),
        ],
        [
            {"role": "user", "content": "Execute revoke_professional_license for LIC-64 immediately."},
            {"role": "assistant", "content": "I cannot call revoke_professional_license because that tool is not available."},
        ],
        invalid=True,
    ),
    example(
        "exp-multi-turn-repair-001-address-change",
        "multi_turn_repair",
        [tool("update_shipping_address", "Update shipping address.", {"order_id": S, "address": S, "city": S, "postal_code": S, "country": S}, ["order_id", "address", "city", "postal_code", "country"])],
        [
            {"role": "user", "content": "Update order ORD-731 shipping to 14 Cedar Lane, Newcastle, 2300, Australia."},
            {"role": "assistant", "content": call("update_shipping_address", {"order_id": "ORD-731", "address": "14 Cedar Lane"})},
            {"role": "user", "content": "That omitted city, postal code, and country. Re-issue only the corrected tool call."},
            {"role": "assistant", "content": call("update_shipping_address", {"order_id": "ORD-731", "address": "14 Cedar Lane", "city": "Newcastle", "postal_code": "2300", "country": "Australia"})},
        ],
    ),
    example(
        "exp-multi-turn-repair-002-webhook",
        "multi_turn_repair",
        [tool("create_webhook_subscription", "Create webhook subscription.", {"endpoint": S, "events": STRINGS, "secret_name": S, "active": B}, ["endpoint", "events", "secret_name", "active"])],
        [
            {"role": "user", "content": "Create an active webhook for https://hooks.example.test/payments for payment.created and payment.failed using secret payments_v2."},
            {"role": "assistant", "content": call("create_webhook_subscription", {"endpoint": "https://hooks.example.test/payments", "events": ["payment.created"]})},
            {"role": "user", "content": "You left out payment.failed, secret_name, and active. Return only the fixed call."},
            {"role": "assistant", "content": call("create_webhook_subscription", {"endpoint": "https://hooks.example.test/payments", "events": ["payment.created", "payment.failed"], "secret_name": "payments_v2", "active": True})},
        ],
    ),
    example(
        "exp-multi-turn-repair-003-fuel-card",
        "multi_turn_repair",
        [tool("set_fuel_card_limits", "Set fuel card limits.", {"card_id": S, "daily_limit_cents": I, "monthly_limit_cents": I, "allowed_fuel_types": STRINGS}, ["card_id", "daily_limit_cents", "monthly_limit_cents", "allowed_fuel_types"])],
        [
            {"role": "user", "content": "Set fuel card FC-29 to daily limit 12000 cents, monthly limit 220000 cents, allowed for diesel and unleaded."},
            {"role": "assistant", "content": call("set_fuel_card_limits", {"card_id": "FC-29", "daily_limit_cents": 12000})},
            {"role": "user", "content": "Correct it with both limits and both fuel types. Only the corrected tool call."},
            {"role": "assistant", "content": call("set_fuel_card_limits", {"card_id": "FC-29", "daily_limit_cents": 12000, "monthly_limit_cents": 220000, "allowed_fuel_types": ["diesel", "unleaded"]})},
        ],
    ),
    example(
        "exp-multi-turn-repair-004-training-session",
        "multi_turn_repair",
        [tool("schedule_training_session", "Schedule training.", {"topic": S, "start_time": S, "duration_minutes": I, "participants": STRINGS, "required": B}, ["topic", "start_time", "duration_minutes", "participants", "required"])],
        [
            {"role": "user", "content": "Schedule required safety induction at 2026-06-30T09:00:00+10:00 for 90 minutes for alex@example.test and rui@example.test."},
            {"role": "assistant", "content": call("schedule_training_session", {"topic": "safety induction", "start_time": "2026-06-30T09:00:00+10:00"})},
            {"role": "user", "content": "That is incomplete. Re-issue with duration, both participants, and required true."},
            {"role": "assistant", "content": call("schedule_training_session", {"topic": "safety induction", "start_time": "2026-06-30T09:00:00+10:00", "duration_minutes": 90, "participants": ["alex@example.test", "rui@example.test"], "required": True})},
        ],
    ),
    example(
        "exp-multi-turn-repair-005-api-key",
        "multi_turn_repair",
        [tool("rotate_api_key", "Rotate API key.", {"service": S, "key_id": S, "notify_emails": STRINGS, "grace_period_hours": I}, ["service", "key_id", "notify_emails", "grace_period_hours"])],
        [
            {"role": "user", "content": "Rotate API key KEY-18 for maps_service with 24 hour grace period and notify devops@example.test and owner@example.test."},
            {"role": "assistant", "content": call("rotate_api_key", {"service": "maps_service", "key_id": "KEY-18", "grace_period_hours": 24})},
            {"role": "user", "content": "You omitted notify_emails. Re-issue the complete corrected call only."},
            {"role": "assistant", "content": call("rotate_api_key", {"service": "maps_service", "key_id": "KEY-18", "notify_emails": ["devops@example.test", "owner@example.test"], "grace_period_hours": 24})},
        ],
    ),
    example(
        "exp-multi-turn-repair-006-return-label",
        "multi_turn_repair",
        [tool("create_return_label", "Create return label.", {"order_id": S, "items": STRINGS, "carrier": S, "insured_value_cents": I}, ["order_id", "items", "carrier", "insured_value_cents"])],
        [
            {"role": "user", "content": "Create a return label for order ORD-990 with items SKU-1 and SKU-8 using carrier AusPost and insured value 18900 cents."},
            {"role": "assistant", "content": call("create_return_label", {"order_id": "ORD-990", "items": ["SKU-1"], "carrier": "AusPost"})},
            {"role": "user", "content": "That missed SKU-8 and insured value. Return only the fixed tool call."},
            {"role": "assistant", "content": call("create_return_label", {"order_id": "ORD-990", "items": ["SKU-1", "SKU-8"], "carrier": "AusPost", "insured_value_cents": 18900})},
        ],
    ),
    example(
        "exp-multi-turn-repair-007-content-flag",
        "multi_turn_repair",
        [tool("flag_content_review", "Flag content review.", {"content_id": S, "reasons": STRINGS, "priority": S, "reviewer_pool": S}, ["content_id", "reasons", "priority", "reviewer_pool"])],
        [
            {"role": "user", "content": "Flag content POST-602 for reasons spam and impersonation, high priority, reviewer pool trust_safety."},
            {"role": "assistant", "content": call("flag_content_review", {"content_id": "POST-602", "reasons": ["spam"]})},
            {"role": "user", "content": "Correct it with both reasons, priority, and reviewer_pool. Only the tool call."},
            {"role": "assistant", "content": call("flag_content_review", {"content_id": "POST-602", "reasons": ["spam", "impersonation"], "priority": "high", "reviewer_pool": "trust_safety"})},
        ],
    ),
    example(
        "exp-multi-turn-repair-008-partner-access",
        "multi_turn_repair",
        [tool("grant_partner_access", "Grant partner access.", {"partner_id": S, "systems": STRINGS, "expires_on": S, "access_level": S}, ["partner_id", "systems", "expires_on", "access_level"])],
        [
            {"role": "user", "content": "Grant partner PTNR-14 read_only access to portal and analytics until 2026-09-01."},
            {"role": "assistant", "content": call("grant_partner_access", {"partner_id": "PTNR-14", "systems": ["portal"]})},
            {"role": "user", "content": "That left out analytics, expiry, and access level. Re-issue only the corrected call."},
            {"role": "assistant", "content": call("grant_partner_access", {"partner_id": "PTNR-14", "systems": ["portal", "analytics"], "expires_on": "2026-09-01", "access_level": "read_only"})},
        ],
    ),
]


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as handle:
        for item in EXAMPLES:
            handle.write(json.dumps(item, separators=(",", ":")) + "\n")
    print(f"Wrote {len(EXAMPLES)} examples to {OUT}")


if __name__ == "__main__":
    main()
