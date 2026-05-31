"""
Demo seed script — populates the database with realistic test data for WUTS.
Run with:  python seed_demo.py
"""
import json
from datetime import datetime, timedelta
from app import create_app
from app.extensions import db
from app.models.job_run import JobRun
from app.models.conflict_log import ConflictLog
from app.models.headcount_record import HeadcountRecord
from app.models.medic_record import MedicRecord
from app.models.periodic_record import PeriodicRecord
from app.models.record_change_log import RecordChangeLog

app = create_app()

def _dt(days_ago=0):
    return datetime.utcnow() - timedelta(days=days_ago)

def _due(days_from_now):
    return (_dt() + timedelta(days=days_from_now)).strftime("%d-%b-%Y")

def seed():
    with app.app_context():
        # ── Wipe existing demo data ──────────────────────────────────────────
        for model in [RecordChangeLog, ConflictLog, HeadcountRecord,
                      MedicRecord, PeriodicRecord, JobRun]:
            model.query.delete()
        db.session.commit()

        # ── 1. Job Runs ──────────────────────────────────────────────────────
        job_runs = [
            JobRun(task_name="headcount",      status="done",    duration_s=12.4,  started_at=_dt(1),  finished_at=_dt(1)-timedelta(seconds=-12), notes="14 flags raised"),
            JobRun(task_name="medic",          status="done",    duration_s=8.1,   started_at=_dt(1),  finished_at=_dt(1)-timedelta(seconds=-8),  notes="6 mismatches found"),
            JobRun(task_name="booking_alerts", status="done",    duration_s=3.2,   started_at=_dt(2),  finished_at=_dt(2)-timedelta(seconds=-3),  notes="9 overdue employees"),
            JobRun(task_name="headcount",      status="warning", duration_s=15.0,  started_at=_dt(3),  finished_at=_dt(3)-timedelta(seconds=-15), notes="Source file had blank rows"),
            JobRun(task_name="medic",          status="failed",  duration_s=None,  started_at=_dt(5),  finished_at=_dt(5)-timedelta(seconds=-1),  notes="MEDIC_ID file not found"),
            JobRun(task_name="pdf",            status="done",    duration_s=22.7,  started_at=_dt(7),  finished_at=_dt(7)-timedelta(seconds=-23), notes="Biometric PDF processed"),
            JobRun(task_name="inbox",          status="done",    duration_s=5.5,   started_at=_dt(7),  finished_at=_dt(7)-timedelta(seconds=-6),  notes="3 booking emails parsed"),
            JobRun(task_name="booking_alerts", status="done",    duration_s=4.0,   started_at=_dt(10), finished_at=_dt(10)-timedelta(seconds=-4), notes=None),
            JobRun(task_name="headcount",      status="done",    duration_s=11.9,  started_at=_dt(14), finished_at=_dt(14)-timedelta(seconds=-12), notes="No new flags"),
            JobRun(task_name="full_cycle",     status="done",    duration_s=19.3,  started_at=_dt(21), finished_at=_dt(21)-timedelta(seconds=-19), notes="Weekly full cycle"),
        ]
        db.session.add_all(job_runs)
        db.session.flush()   # get IDs

        hc_job  = job_runs[0]
        med_job = job_runs[1]

        # ── 2. Headcount Records ─────────────────────────────────────────────
        headcount_records = [
            # New hires not yet in medical system
            HeadcountRecord(personnel_name="MOENG TEBOGO",        employee_number="EMP-20241",  department="Mining Operations",  personnel_subarea="Jwaneng Mine", position="Mining Engineer",       section="Production",    sub_section="Drill & Blast", ps_group="P3", age=29, flag_type="new",       flagged_on=_dt(1),  source_file="Headcount_Apr2026.xlsx", resolved=False, job_run_id=hc_job.id),
            HeadcountRecord(personnel_name="SEKGOBELA NALEDI",     employee_number="EMP-20242",  department="Human Resources",    personnel_subarea="Head Office",  position="HR Officer",            section="Recruitment",   sub_section=None,            ps_group="P2", age=25, flag_type="new",       flagged_on=_dt(1),  source_file="Headcount_Apr2026.xlsx", resolved=False, job_run_id=hc_job.id),
            HeadcountRecord(personnel_name="KGOMOTSO SITHOLE",     employee_number="EMP-20243",  department="Engineering",        personnel_subarea="Orapa Mine",   position="Electrician",           section="Maintenance",   sub_section="HV Systems",    ps_group="T2", age=34, flag_type="new",       flagged_on=_dt(1),  source_file="Headcount_Apr2026.xlsx", resolved=False, job_run_id=hc_job.id),
            HeadcountRecord(personnel_name="DIPUO RAMADUBU",       employee_number="EMP-20244",  department="Security",           personnel_subarea="Jwaneng Mine", position="Security Officer",      section="Access Control",sub_section=None,            ps_group="T1", age=31, flag_type="new",       flagged_on=_dt(1),  source_file="Headcount_Apr2026.xlsx", resolved=False, job_run_id=hc_job.id),
            # Suspected resignations / exits not yet processed
            HeadcountRecord(personnel_name="LETSATSI GAOLATHE",    employee_number="EMP-18344",  department="Finance",            personnel_subarea="Head Office",  position="Financial Analyst",     section="Treasury",      sub_section=None,            ps_group="P2", age=41, flag_type="resigned",  flagged_on=_dt(2),  source_file="Headcount_Apr2026.xlsx", resolved=False, job_run_id=hc_job.id),
            HeadcountRecord(personnel_name="OBAKENG SETHIBE",      employee_number="EMP-17001",  department="Mining Operations",  personnel_subarea="Orapa Mine",   position="Shift Supervisor",      section="Processing",    sub_section="Conveyor",      ps_group="P4", age=47, flag_type="resigned",  flagged_on=_dt(2),  source_file="Headcount_Apr2026.xlsx", resolved=False, job_run_id=hc_job.id),
            # Duplicate entries across systems
            HeadcountRecord(personnel_name="KAGISO MOLEFE",        employee_number="EMP-15209",  department="IT",                 personnel_subarea="Head Office",  position="Systems Administrator", section="Infrastructure", sub_section=None,           ps_group="P3", age=37, flag_type="duplicate", flagged_on=_dt(3),  source_file="Headcount_Apr2026.xlsx", resolved=False, job_run_id=hc_job.id),
            HeadcountRecord(personnel_name="KAGISO MOLEFE",        employee_number="EMP-15209B", department="IT",                 personnel_subarea="Head Office",  position="Systems Administrator", section="Infrastructure", sub_section=None,           ps_group="P3", age=37, flag_type="duplicate", flagged_on=_dt(3),  source_file="Headcount_Apr2026.xlsx", resolved=False, job_run_id=hc_job.id),
            # Suspicious — on leave but not in medical schedule
            HeadcountRecord(personnel_name="BOITUMELO NKWE",       employee_number="EMP-16788",  department="Health Services",    personnel_subarea="Jwaneng Mine", position="Nurse",                 section="Clinic",        sub_section=None,            ps_group="P3", age=39, flag_type="suspicious",flagged_on=_dt(4),  source_file="Headcount_Apr2026.xlsx", resolved=False, job_run_id=hc_job.id),
            # Already resolved example
            HeadcountRecord(personnel_name="THABO MOLEFI",         employee_number="EMP-14500",  department="Engineering",        personnel_subarea="Jwaneng Mine", position="Mechanical Engineer",   section="Maintenance",   sub_section="Rotating Equip",ps_group="P3", age=44, flag_type="new",       flagged_on=_dt(10), source_file="Headcount_Mar2026.xlsx", resolved=True,  job_run_id=hc_job.id),
        ]
        db.session.add_all(headcount_records)

        # ── 3. Medic Records ─────────────────────────────────────────────────
        medic_records = [
            MedicRecord(personnel_name="BALESENG PHIRI",      employee_number="EMP-12301", department="Mining Operations", personnel_subarea="Jwaneng Mine", position="Blasting Technician",  ps_group="T3", record_type="mismatch", date_in_periodics="15-Jan-2026", date_in_medic_id="20-Jan-2026", date_to_update_to="20-Jan-2026", difference_days=5,   type_of_medical="Periodic",      last_medical_periodics="15-Jan-2026", exit_status=None,      flagged_on=_dt(1),  resolved=False, source_file="MEDIC_ID_Apr2026.xlsx", job_run_id=med_job.id),
            MedicRecord(personnel_name="GORATA TLHAGOANE",    employee_number="EMP-13450", department="Engineering",       personnel_subarea="Orapa Mine",   position="Welder",               ps_group="T2", record_type="mismatch", date_in_periodics="02-Feb-2026", date_in_medic_id="14-Feb-2026", date_to_update_to="14-Feb-2026", difference_days=12,  type_of_medical="Periodic",      last_medical_periodics="02-Feb-2026", exit_status=None,      flagged_on=_dt(1),  resolved=False, source_file="MEDIC_ID_Apr2026.xlsx", job_run_id=med_job.id),
            MedicRecord(personnel_name="MPHO SELEPE",         employee_number="EMP-11987", department="Processing",        personnel_subarea="Jwaneng Mine", position="Plant Operator",       ps_group="T2", record_type="missing",  date_in_periodics=None,          date_in_medic_id="10-Mar-2026", date_to_update_to="10-Mar-2026", difference_days=None,type_of_medical="Entry",         last_medical_periodics=None,          exit_status=None,      flagged_on=_dt(1),  resolved=False, source_file="MEDIC_ID_Apr2026.xlsx", job_run_id=med_job.id),
            MedicRecord(personnel_name="TUMELO RADITLHALO",   employee_number="EMP-10044", department="Mining Operations", personnel_subarea="Jwaneng Mine", position="Drill Operator",       ps_group="T3", record_type="exited",   date_in_periodics="05-Dec-2025", date_in_medic_id="05-Dec-2025", date_to_update_to=None,          difference_days=0,   type_of_medical="Periodic",      last_medical_periodics="05-Dec-2025", exit_status="Resigned",flagged_on=_dt(2),  resolved=False, source_file="MEDIC_ID_Apr2026.xlsx", job_run_id=med_job.id),
            MedicRecord(personnel_name="LESEGO SEGWAGWE",     employee_number="EMP-14102", department="Health Services",   personnel_subarea="Orapa Mine",   position="Paramedic",            ps_group="P2", record_type="mismatch", date_in_periodics="01-Mar-2026", date_in_medic_id="18-Mar-2026", date_to_update_to="18-Mar-2026", difference_days=17,  type_of_medical="Periodic",      last_medical_periodics="01-Mar-2026", exit_status=None,      flagged_on=_dt(2),  resolved=False, source_file="MEDIC_ID_Apr2026.xlsx", job_run_id=med_job.id),
            MedicRecord(personnel_name="KEITUMELE MODISE",    employee_number="EMP-16230", department="Security",          personnel_subarea="Jwaneng Mine", position="Guard Supervisor",     ps_group="T2", record_type="missing",  date_in_periodics=None,          date_in_medic_id="22-Apr-2026", date_to_update_to="22-Apr-2026", difference_days=None,type_of_medical="Entry",         last_medical_periodics=None,          exit_status=None,      flagged_on=_dt(3),  resolved=False, source_file="MEDIC_ID_Apr2026.xlsx", job_run_id=med_job.id),
        ]
        db.session.add_all(medic_records)

        # ── 4. Periodic Records ──────────────────────────────────────────────
        periodic_records = [
            # Overdue (negative days_remaining)
            PeriodicRecord(employee_number="EMP-10001", personnel_name="MPHO DITHEBE",       surname="DITHEBE",    gender="Male",   role="Shaft Sinker",        department="Mining Operations", subarea="Jwaneng Mine", ps_group="T3", grade="T3A", base="Jwaneng",   date_done="10-Apr-2025", next_due=_due(-45),  update_status="Overdue",   update_date=None, days_remaining=-45, status_flag="OVERDUE",    clinic="Jwaneng Clinic",   needs_review="Yes", review_reason="Exam overdue by 45 days",             form_type="Periodic", source_file="DCC_PERIODICS_Apr2026.xlsx"),
            PeriodicRecord(employee_number="EMP-10002", personnel_name="OTENG KEBONANG",     surname="KEBONANG",   gender="Male",   role="Underground Blaster", department="Mining Operations", subarea="Jwaneng Mine", ps_group="T3", grade="T3B", base="Jwaneng",   date_done="22-Jan-2025", next_due=_due(-90),  update_status="Overdue",   update_date=None, days_remaining=-90, status_flag="OVERDUE",    clinic="Jwaneng Clinic",   needs_review="Yes", review_reason="Exam overdue by 90 days — escalate",  form_type="Periodic", source_file="DCC_PERIODICS_Apr2026.xlsx"),
            PeriodicRecord(employee_number="EMP-10003", personnel_name="GAOPALELWE SETLHARE",surname="SETLHARE",  gender="Female", role="Lab Technician",      department="Geology",           subarea="Orapa Mine",   ps_group="P2", grade="P2A", base="Orapa",     date_done="01-Mar-2025", next_due=_due(-12),  update_status="Overdue",   update_date=None, days_remaining=-12, status_flag="OVERDUE",    clinic="Orapa Clinic",     needs_review="Yes", review_reason="Exam overdue by 12 days",             form_type="Periodic", source_file="DCC_PERIODICS_Apr2026.xlsx"),
            PeriodicRecord(employee_number="EMP-10004", personnel_name="NTLHANTLHE RAKOPS",  surname="RAKOPS",    gender="Male",   role="Processing Operator", department="Processing",        subarea="Jwaneng Mine", ps_group="T2", grade="T2A", base="Jwaneng",   date_done="15-Feb-2025", next_due=_due(-3),   update_status="Overdue",   update_date=None, days_remaining=-3,  status_flag="OVERDUE",    clinic="Jwaneng Clinic",   needs_review="No",  review_reason=None,                                  form_type="Periodic", source_file="DCC_PERIODICS_Apr2026.xlsx"),
            # Due soon (within 30 days)
            PeriodicRecord(employee_number="EMP-10005", personnel_name="ONALENNA MODISANE",  surname="MODISANE",  gender="Female", role="HR Specialist",       department="Human Resources",   subarea="Head Office",  ps_group="P3", grade="P3A", base="Head Office",date_done="08-May-2025", next_due=_due(7),    update_status="Pending",   update_date=None, days_remaining=7,   status_flag="DUE_SOON",   clinic="Gaborone Clinic",  needs_review="No",  review_reason=None,                                  form_type="Periodic", source_file="DCC_PERIODICS_Apr2026.xlsx"),
            PeriodicRecord(employee_number="EMP-10006", personnel_name="BAAGI GAOLEKWE",     surname="GAOLEKWE",  gender="Male",   role="Electrician",         department="Engineering",       subarea="Orapa Mine",   ps_group="T2", grade="T2B", base="Orapa",     date_done="12-May-2025", next_due=_due(15),   update_status="Pending",   update_date=None, days_remaining=15,  status_flag="DUE_SOON",   clinic="Orapa Clinic",     needs_review="No",  review_reason=None,                                  form_type="Periodic", source_file="DCC_PERIODICS_Apr2026.xlsx"),
            PeriodicRecord(employee_number="EMP-10007", personnel_name="SEIPATI MOKWENA",    surname="MOKWENA",   gender="Female", role="Safety Officer",      department="Health & Safety",   subarea="Jwaneng Mine", ps_group="P2", grade="P2B", base="Jwaneng",   date_done="25-May-2025", next_due=_due(22),   update_status="Pending",   update_date=None, days_remaining=22,  status_flag="DUE_SOON",   clinic="Jwaneng Clinic",   needs_review="No",  review_reason=None,                                  form_type="Periodic", source_file="DCC_PERIODICS_Apr2026.xlsx"),
            PeriodicRecord(employee_number="EMP-10008", personnel_name="KHUMO NTSIMANE",     surname="NTSIMANE",  gender="Male",   role="Mechanical Fitter",   department="Engineering",       subarea="Jwaneng Mine", ps_group="T2", grade="T2A", base="Jwaneng",   date_done="01-Jun-2025", next_due=_due(28),   update_status="Pending",   update_date=None, days_remaining=28,  status_flag="DUE_SOON",   clinic="Jwaneng Clinic",   needs_review="No",  review_reason=None,                                  form_type="Periodic", source_file="DCC_PERIODICS_Apr2026.xlsx"),
            # Up to date
            PeriodicRecord(employee_number="EMP-10009", personnel_name="TSHEPO GAREFELO",    surname="GAREFELO",  gender="Male",   role="Mine Surveyor",       department="Mining Operations", subarea="Jwaneng Mine", ps_group="P4", grade="P4A", base="Jwaneng",   date_done="15-Jan-2026", next_due=_due(180),  update_status="Current",   update_date="15-Jan-2026", days_remaining=180, status_flag="OK",       clinic="Jwaneng Clinic",   needs_review="No",  review_reason=None,                                  form_type="Periodic", source_file="DCC_PERIODICS_Apr2026.xlsx"),
            PeriodicRecord(employee_number="EMP-10010", personnel_name="PATIENCE KOLOTI",    surname="KOLOTI",    gender="Female", role="Accountant",          department="Finance",           subarea="Head Office",  ps_group="P3", grade="P3B", base="Head Office",date_done="20-Feb-2026", next_due=_due(245),  update_status="Current",   update_date="20-Feb-2026", days_remaining=245, status_flag="OK",       clinic="Gaborone Clinic",  needs_review="No",  review_reason=None,                                  form_type="Periodic", source_file="DCC_PERIODICS_Apr2026.xlsx"),
            PeriodicRecord(employee_number="EMP-10011", personnel_name="LEBO RAMOGOTSI",     surname="RAMOGOTSI", gender="Male",   role="Security Guard",      department="Security",          subarea="Orapa Mine",   ps_group="T1", grade="T1A", base="Orapa",     date_done="05-Mar-2026", next_due=_due(320),  update_status="Current",   update_date="05-Mar-2026", days_remaining=320, status_flag="OK",       clinic="Orapa Clinic",     needs_review="No",  review_reason=None,                                  form_type="Periodic", source_file="DCC_PERIODICS_Apr2026.xlsx"),
            PeriodicRecord(employee_number="EMP-10012", personnel_name="GOITSEONE SELELO",   surname="SELELO",    gender="Female", role="Nurse",               department="Health Services",   subarea="Jwaneng Mine", ps_group="P3", grade="P3A", base="Jwaneng",   date_done="10-Apr-2026", next_due=_due(355),  update_status="Current",   update_date="10-Apr-2026", days_remaining=355, status_flag="OK",       clinic="Jwaneng Clinic",   needs_review="No",  review_reason=None,                                  form_type="Periodic", source_file="DCC_PERIODICS_Apr2026.xlsx"),
            PeriodicRecord(employee_number="EMP-10013", personnel_name="REFILWE SEOKOLWE",   surname="SEOKOLWE",  gender="Male",   role="IT Support Analyst",  department="IT",                subarea="Head Office",  ps_group="P2", grade="P2A", base="Head Office",date_done="01-Apr-2026", next_due=_due(346),  update_status="Current",   update_date="01-Apr-2026", days_remaining=346, status_flag="OK",       clinic="Gaborone Clinic",  needs_review="No",  review_reason=None,                                  form_type="Periodic", source_file="DCC_PERIODICS_Apr2026.xlsx"),
        ]
        db.session.add_all(periodic_records)

        # ── 5. Conflict Logs ─────────────────────────────────────────────────
        conflict_logs = [
            ConflictLog(source="headcount", description="EMP-15209 (KAGISO MOLEFE) appears twice with different employee numbers. Possible duplicate registration — verify with HR.", resolved=False, logged_at=_dt(3)),
            ConflictLog(source="medic",     description="BALESENG PHIRI (EMP-12301): Exam date differs by 5 days between DCC PERIODICS and MEDIC ID. Likely data entry error — update PERIODICS.", resolved=False, logged_at=_dt(1)),
            ConflictLog(source="medic",     description="MPHO SELEPE (EMP-11987) has an entry medical in MEDIC ID but no corresponding record in DCC PERIODICS. Record needs to be created.", resolved=False, logged_at=_dt(1)),
            ConflictLog(source="headcount", description="LETSATSI GAOLATHE (EMP-18344) absent from last 3 headcount cycles. Possible undeclared resignation — confirm with Finance dept.", resolved=False, logged_at=_dt(2)),
            ConflictLog(source="booking_alerts", description="9 employees in Jwaneng Mine have medical exams overdue by more than 30 days. Bookings not yet confirmed for Q2 2026 cycle.", resolved=False, logged_at=_dt(2)),
            ConflictLog(source="headcount", description="BOITUMELO NKWE (EMP-16788) is listed as active in headcount but does not appear in the medical scheduling system.", resolved=False, logged_at=_dt(4)),
        ]
        db.session.add_all(conflict_logs)

        # ── 6. Record Change Logs (audit trail) ──────────────────────────────
        change_logs = [
            RecordChangeLog(record_source="periodic",  record_id=9,  employee_number="EMP-10009", personnel_name="TSHEPO GAREFELO",  changed_fields=json.dumps({"next_due": {"from": "15-Jan-2026", "to": "15-Jan-2027"}, "days_remaining": {"from": "-5", "to": "180"}}),              change_reason="Date incorrectly entered as 2026 instead of 2027 during import.", changed_at=_dt(5)),
            RecordChangeLog(record_source="periodic",  record_id=10, employee_number="EMP-10010", personnel_name="PATIENCE KOLOTI",  changed_fields=json.dumps({"update_status": {"from": "Pending", "to": "Current"}, "date_done": {"from": "None", "to": "20-Feb-2026"}}),         change_reason="Exam completed at Gaborone Clinic — confirmed by clinic coordinator.", changed_at=_dt(3)),
            RecordChangeLog(record_source="headcount", record_id=10, employee_number="EMP-14500", personnel_name="THABO MOLEFI",     changed_fields=json.dumps({"resolved": {"from": "false", "to": "true"}}),                                                                        change_reason="New hire confirmed as onboarded. Medical exam scheduled for 05-May-2026.", changed_at=_dt(8)),
        ]
        db.session.add_all(change_logs)

        db.session.commit()
        print("Demo data seeded successfully.")
        print(f"  Job runs:           {len(job_runs)}")
        print(f"  Headcount records:  {len(headcount_records)}")
        print(f"  Medic records:      {len(medic_records)}")
        print(f"  Periodic records:   {len(periodic_records)}")
        print(f"  Conflict logs:      {len(conflict_logs)}")
        print(f"  Change logs:        {len(change_logs)}")


if __name__ == "__main__":
    seed()
