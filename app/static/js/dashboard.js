 // CSRF PATCH
function csrfToken(){
      return document.querySelector('meta[name="csrf-token"]').content;

      
    }

function dashboard() {
  return {
    metrics:             {},
    jobs:                [],
    taskSummary:         [],
    newHires:            [],
    departmentBreakdown: [],
    datetime:            "",
    running:       {},
    historySearch: "",
    historyStatus: "",
    conflicts:            [],
    conflictLoading:      false,
    conflictError:        "",
    conflictShowResolved: false,
    conflictSourceFilter: "",
    conflictResolvingId:  null,
    activeStatusFilter: "overdue",
    employeeStatusRecords: [],
    employeeStatusLoading: false,
    employeeStatusError: "",
    employeeSearchQuery: "",
    employeeSearchResults: [],
    employeeSearchLoading: false,
    employeeSearchError: "",
    employeeFilterOpen: false,
    employeeFilters: { department: "", subarea: "", role: "", ps_group: "" },
    employeeStatusOptions: {
      periodic: {},
      headcount: {},
    },
    activeChangeLogSource: "all",
    changeLogs: [],
    changeLogLoading: false,
    changeLogError: "",
    employeeStatusEditingKey: null,
    employeeStatusDraft: {},
    employeeStatusEditReason: "",
    employeeStatusSaving: false,
    employeeStatusSaveError: "",
    periodicStatusFields: [
      { key: "personnel_name", label: "Employee", type: "text" },
      { key: "employee_number", label: "Employee Number", type: "text" },
      { key: "gender", label: "Gender", type: "select", options: ["Male", "Female"] },
      { key: "role", label: "Position", type: "text" },
      { key: "department", label: "Department", type: "select" },
      { key: "subarea", label: "Sub Area", type: "select" },
      { key: "ps_group", label: "PS Group", type: "select" },
      { key: "grade", label: "Grade", type: "select" },
      { key: "base", label: "Base", type: "select" },
      { key: "date_done", label: "Last Medical", type: "date" },
      { key: "next_due", label: "Next Due", type: "date" },
      { key: "update_status", label: "Update Status", type: "select" },
      { key: "update_date", label: "Update Date", type: "date" },
      { key: "days_remaining", label: "Days Remaining", type: "number" },
      { key: "status_flag", label: "Status Flag", type: "select" },
      { key: "fallback_used", label: "Fallback Used", type: "text" },
      { key: "source_file", label: "Source File", type: "text" },
      { key: "form_type", label: "Form Type", type: "text" },
      { key: "surname", label: "Surname", type: "text" },
      { key: "clinic", label: "Clinic", type: "select" },
      { key: "needs_review", label: "Needs Review", type: "text" },
      { key: "review_reason", label: "Review Reason", type: "text" },
    ],
    headcountStatusFields: [
      { key: "personnel_name", label: "Employee", type: "text" },
      { key: "employee_number", label: "Employee Number", type: "text" },
      { key: "department", label: "Department", type: "select" },
      { key: "personnel_subarea", label: "Sub Area", type: "select" },
      { key: "position", label: "Position", type: "select" },
      { key: "section", label: "Section", type: "select" },
      { key: "sub_section", label: "Sub Section", type: "select" },
      { key: "ps_group", label: "PS Group", type: "select" },
      { key: "age", label: "Age", type: "number" },
      { key: "flag_type", label: "Flag Type", type: "select", options: ["new", "moved", "exited", "updated"] },
      { key: "flagged_on", label: "Flagged On", type: "date" },
      { key: "source_file", label: "Source File", type: "text" },
      { key: "resolved", label: "Resolved", type: "checkbox" },
      { key: "job_run_id", label: "Job Run ID", type: "number" },
    ],

    // CSRF PATCH

   

    // ── Biometric review modal ─────────────────────────────
    bioModal: {
      open:     false,
      loading:  false,
      error:    "",
      data:     {},
      filePath: "",
    },

    // ── File picker modal ──────────────────────────────────
    modal: {
      open:     false,
      task:     "",
      folder:   "",
      files:    [],
      loading:  false,
      error:    "",
    },

    init() {
      this.updateTime();
      this.fetchMetrics();
      this.fetchJobs();
      this.fetchTaskSummary();
      this.fetchNewHires();
      this.fetchDepartmentBreakdown();
      setInterval(() => {
        this.fetchMetrics();
        this.fetchJobs();
        this.fetchTaskSummary();
        this.fetchNewHires();
        this.fetchDepartmentBreakdown();
      }, 30000);
      setInterval(() => this.updateTime(), 1000);
    },

    initEmployeeStatus(category = "overdue") {
      this.updateTime();
      this.activeStatusFilter = category;
      this.fetchEmployeeStatusOptions();
      this.fetchEmployeeStatus(category);
      setInterval(() => this.updateTime(), 1000);
    },

    initChangeLog(source = "all") {
      this.updateTime();
      this.activeChangeLogSource = source;
      this.fetchChangeLogs(source);
      setInterval(() => this.updateTime(), 1000);
    },

    initConflicts() {
      this.updateTime();
      this.fetchConflicts();
      setInterval(() => this.updateTime(), 1000);
    },

    fetchConflicts() {
      this.conflictLoading = true;
      this.conflictError = "";
      const url = `/api/conflicts?resolved=${this.conflictShowResolved}`;
      fetch(url)
        .then(r => r.json())
        .then(data => {
          this.conflictLoading = false;
          if (data.error) {
            this.conflictError = data.error;
          } else {
            this.conflicts = data;
          }
        })
        .catch(err => {
          this.conflictLoading = false;
          this.conflictError = err.message;
        });
    },

    get filteredConflicts() {
      return this.conflicts.filter(c =>
        !this.conflictSourceFilter || c.source === this.conflictSourceFilter
      );
    },

    resolveConflict(conflict) {
      this.conflictResolvingId = conflict.id;
      fetch(`/api/conflicts/${conflict.id}/resolve`, {
        method: "PATCH",
        headers: { "X-CSRFToken": csrfToken() },
      })
        .then(r => r.json())
        .then(updated => {
          this.conflictResolvingId = null;
          const idx = this.conflicts.findIndex(c => c.id === conflict.id);
          if (idx !== -1) this.conflicts[idx] = updated;
          this.fetchMetrics();
        })
        .catch(() => { this.conflictResolvingId = null; });
    },

    conflictSourceLabel(source) {
      return { headcount: "Headcount", medic: "Medic", booking_alerts: "Booking" }[source] || source;
    },

    conflictSourceClass(source) {
      return { headcount: "p-warn", medic: "p-err", booking_alerts: "p-run" }[source] || "";
    },

    fetchMetrics() {
      fetch("/api/metrics")
        .then(r => r.json())
        .then(data => { this.metrics = data; });
    },

    fetchJobs() {
      const onHistory = window.location.pathname === "/history";
      fetch(onHistory ? "/api/jobs?limit=500" : "/api/jobs")
        .then(r => r.json())
        .then(data => { this.jobs = data; });
    },

    get filteredJobs() {
      return this.jobs.filter(j => {
        const matchSearch = !this.historySearch ||
          j.task_name.toLowerCase().includes(this.historySearch.toLowerCase()) ||
          (j.notes || "").toLowerCase().includes(this.historySearch.toLowerCase());
        const matchStatus = !this.historyStatus || j.status === this.historyStatus;
        return matchSearch && matchStatus;
      });
    },

    get latestJob() {
      return this.jobs.length ? this.jobs[0] : null;
    },

    get attentionCount() {
      return (this.metrics.overdue ?? 0) + (this.metrics.due_soon ?? 0) + (this.metrics.pending_hires ?? 0) + (this.metrics.medic_flags ?? 0);
    },

    get latestResultMessage() {
      if (!this.latestJob) return "";
      if (this.latestJob.notes) return this.latestJob.notes;
      if (this.latestJob.status === "done") return "The latest task completed successfully.";
      if (this.latestJob.status === "failed") return "The latest task did not complete. Review the details and try again.";
      if (this.latestJob.status === "running") return "The latest task is still running.";
      if (this.latestJob.status === "warning") return "The latest task finished with a warning and may need review.";
      return "The latest task has been updated.";
    },

    get nextStepHint() {
      if (!this.latestJob) return "Run a task to begin processing.";
      if (this.latestJob.status === "failed") return "Check the task details and run it again.";
      if (this.latestJob.status === "warning") return "Review the flagged records before continuing.";
      if (this.metrics.pending_hires > 0) return "Book medicals for new hires still waiting.";
      if (this.metrics.overdue > 0) return "Follow up on overdue employees next.";
      return "Open Dashboards or continue with the next update.";
    },

    fetchTaskSummary() {
      fetch("/api/task-summary")
        .then(r => r.json())
        .then(data => { this.taskSummary = data; });
    },

    fetchNewHires() {
      fetch("/api/new-hires")
        .then(r => r.json())
        .then(data => { this.newHires = data; });
    },

    fetchDepartmentBreakdown() {
      fetch("/api/department-breakdown")
        .then(r => r.json())
        .then(data => { if (!data.error) this.departmentBreakdown = data; });
    },

    fetchEmployeeStatus(category = "overdue") {
      this.employeeStatusLoading = true;
      this.employeeStatusError = "";
      fetch(`/api/employee-status?category=${category}`)
        .then(r => r.json())
        .then(data => {
          this.employeeStatusLoading = false;
          if (data.error) {
            this.employeeStatusError = data.error;
          } else {
            this.employeeStatusRecords = data;
          }
        })
        .catch(err => {
          this.employeeStatusLoading = false;
          this.employeeStatusError = err.message;
        });
    },

    fetchEmployeeStatusOptions() {
      fetch("/api/employee-status-options")
        .then(r => r.json())
        .then(data => {
          if (!data.error) {
            this.employeeStatusOptions = {
              periodic: data.periodic || {},
              headcount: data.headcount || {},
            };
          }
        })
        .catch(() => {});
    },

    fetchChangeLogs(source = "all") {
      this.changeLogLoading = true;
      this.changeLogError = "";
      fetch(`/api/record-change-logs?source=${source}`)
        .then(r => r.json())
        .then(data => {
          this.changeLogLoading = false;
          if (data.error) {
            this.changeLogError = data.error;
          } else {
            this.changeLogs = data;
          }
        })
        .catch(err => {
          this.changeLogLoading = false;
          this.changeLogError = err.message;
        });
    },

    setStatusFilter(category) {
      this.activeStatusFilter = category;
      this.closeEmployeeStatusEditor();
      this.clearEmployeeFilters();
      if (category === "search") {
        this.employeeSearchQuery = "";
        this.employeeSearchResults = [];
      } else {
        this.fetchEmployeeStatus(category);
      }
      const url = new URL(window.location.href);
      url.searchParams.set("category", category);
      window.history.replaceState({}, "", url.toString());
    },

    clearEmployeeFilters() {
      this.employeeFilters = { department: "", subarea: "", role: "", ps_group: "" };
    },

    get activeFilterCount() {
      return Object.values(this.employeeFilters).filter(v => v !== "").length;
    },

    get filteredEmployeeStatusRecords() {
      return this.employeeStatusRecords.filter(r => {
        const dept    = this.employeeFilters.department;
        const subarea = this.employeeFilters.subarea;
        const role    = this.employeeFilters.role;
        const ps      = this.employeeFilters.ps_group;
        return (
          (!dept    || (r.department || "") === dept) &&
          (!subarea || (r.subarea || r.personnel_subarea || "") === subarea) &&
          (!role    || (r.role || r.position || "") === role) &&
          (!ps      || (r.ps_group || "") === ps)
        );
      });
    },

    filterOptions(field) {
      const vals = this.employeeStatusRecords
        .map(r => {
          if (field === "department") return r.department;
          if (field === "subarea")    return r.subarea || r.personnel_subarea;
          if (field === "role")       return r.role || r.position;
          if (field === "ps_group")   return r.ps_group;
        })
        .filter(v => v && v.trim() !== "");
      return [...new Set(vals)].sort();
    },

    runEmployeeSearch() {
      const q = (this.employeeSearchQuery || "").trim().toLowerCase();
      if (!q) { this.employeeSearchResults = []; return; }
      this.employeeSearchLoading = true;
      this.employeeSearchError = "";
      const categories = ["overdue", "due_soon", "up_to_date", "new_hires"];
      Promise.all(categories.map(cat =>
        fetch(`/api/employee-status?category=${cat}`).then(r => r.json())
      ))
        .then(results => {
          this.employeeSearchLoading = false;
          const all = results.flat().filter(r => !r.error);
          this.employeeSearchResults = all.filter(r => {
            return (
              (r.personnel_name || "").toLowerCase().includes(q) ||
              String(r.employee_number || "").includes(q) ||
              (r.department || "").toLowerCase().includes(q) ||
              (r.subarea || r.personnel_subarea || "").toLowerCase().includes(q) ||
              (r.role || r.position || "").toLowerCase().includes(q)
            );
          });
        })
        .catch(err => {
          this.employeeSearchLoading = false;
          this.employeeSearchError = err.message;
        });
    },

    setChangeLogSource(source) {
      this.activeChangeLogSource = source;
      this.fetchChangeLogs(source);
      const url = new URL(window.location.href);
      url.searchParams.set("source", source);
      window.history.replaceState({}, "", url.toString());
    },

    get statusPageTitle() {
      return {
        overdue: "Overdue Employees",
        due_soon: "Employees Due Within 30 Days",
        up_to_date: "Employees Up To Date",
        new_hires: "New Hires Needing Booking",
      }[this.activeStatusFilter] || "Employee Status";
    },

    // ── Open file picker for tasks that need a file ────────
    openPicker(task, folder) {
      this.modal.open    = true;
      this.modal.task    = task;
      this.modal.folder  = folder;
      this.modal.files   = [];
      this.modal.error   = "";
      this.modal.loading = true;

      fetch(`/api/files/${folder}`)
        .then(r => r.json())
        .then(data => {
          this.modal.loading = false;
          if (data.error) {
            this.modal.error = data.error;
          } else {
            this.modal.files = data.files;
          }
        });
    },

    closePicker() {
      this.modal.open = false;
    },

    // ── Run task with selected file ────────────────────────
    selectFile(filename) {
      const task   = this.modal.task;
      const folder = this.modal.folder;
      this.modal.open = false;

      fetch(`/api/files/${folder}`)
        .then(r => r.json())
        .then(data => {
          const filePath = data.folder + "\\" + filename;
          if (task === "biometric") {
            this.extractBiometric(filePath);
          } else {
            this.triggerTask(task, filePath);
          }
        });
    },

    // ── Biometric: phase 1 — extract ──────────────────────
    extractBiometric(filePath) {
      this.bioModal.open     = true;
      this.bioModal.loading  = true;
      this.bioModal.error    = "";
      this.bioModal.data     = {};
      this.bioModal.filePath = filePath;

      fetch("/api/biometric/extract", {
        method:  "POST",
        headers: { "Content-Type": "application/json",
          'X-CSRFToken': csrfToken()
         },
        body:    JSON.stringify({ file_path: filePath }),
        

      })
        .then(r => r.json())
        .then(data => {
          this.bioModal.loading = false;
          if (data.error) {
            this.bioModal.error = data.error;
          } else {
            // Format Date object → readable string for the input
            if (data.Date && typeof data.Date === "object") {
              data.Date = new Date(data.Date).toLocaleDateString("en-GB");
            }
            this.bioModal.data = data;
          }
        })
        .catch(err => {
          this.bioModal.loading = false;
          this.bioModal.error   = err.message;
        });
    },

    // ── Biometric: phase 2 — confirm & save ───────────────
    confirmBiometric() {
      fetch("/api/biometric/confirm", {
        method:  "POST",
        headers: { "Content-Type": "application/json",
                   'X-CSRFToken': csrfToken()
        },
        body:    JSON.stringify({
          data:      this.bioModal.data,
          file_path: this.bioModal.filePath,
        }),
      })
        .then(r => r.json())
        .then(() => {
          this.bioModal.open = false;
          this.fetchJobs();
          this.fetchMetrics();
          this.fetchTaskSummary();
        });
    },

    // ── Trigger task (with optional file path) ─────────────
    triggerTask(task, filePath = null) {
      if (this.running[task]) return;
      this.running[task] = true;

      const body = filePath ? JSON.stringify({ file_path: filePath }) : null;

      fetch(`/api/run/${task}`, {
        method:  "POST",
        headers: filePath
          ? { "Content-Type": "application/json", "X-CSRFToken": csrfToken() }
          : { "X-CSRFToken": csrfToken() },
        body:    body,
      })
        .then(r => r.json())
        .then(() => {
          const poll = setInterval(() => {
            this.fetchJobs();
            this.fetchMetrics();
            const latest = this.jobs[0];
            if (latest && latest.status !== "running") {
              clearInterval(poll);
              this.running[task] = false;
            }
          }, 3000);
        });
    },

    updateTime() {
      const now = new Date();
      this.datetime = now.toLocaleString("en-GB", {
        weekday: "long", day: "2-digit",
        month:   "long", year: "numeric",
        hour:    "2-digit", minute: "2-digit"
      });
    },

    statusClass(status) {
      return {
        "p-ok":   status === "done",
        "p-run":  status === "running",
        "p-warn": status === "warning",
        "p-err":  status === "failed",
      };
    },

    displayStatus(status) {
      return {
        done: "Completed",
        running: "In progress",
        warning: "Needs review",
        failed: "Needs attention",
      }[status] || status;
    },

    displayTaskName(task) {
      return {
        inbox: "Check New Emails",
        headcount: "Update Staff List",
        booking_alerts: "Send Booking Reminders",
        pdf: "Process Medical Reports",
        medic: "Review ID Issues",
        biometric: "Biometric Screening",
        full_cycle: "Run All Updates",
      }[task] || task;
    },

    employeeStatusLabel(category) {
      return {
        overdue: "Overdue",
        due_soon: "Due Soon",
        up_to_date: "Up To Date",
        new_hires: "New Hire",
      }[category] || category;
    },

    employeeStatusPillClass(category) {
      return {
        "p-err": category === "overdue" || category === "new_hires",
        "p-warn": category === "due_soon",
        "p-ok": category === "up_to_date",
      };
    },

    humanizeFieldName(field) {
      return String(field || "")
        .replace(/_/g, " ")
        .replace(/\b\w/g, char => char.toUpperCase());
    },

    displayChangeValue(value) {
      if (value === null || value === undefined || value === "") return "-";
      if (typeof value === "boolean") return value ? "Yes" : "No";
      return String(value);
    },

    employeeStatusRecordKey(record) {
      return `${record.source}-${record.id || record.employee_number || record.personnel_name}`;
    },

    isEditingEmployeeStatus(record) {
      return this.employeeStatusEditingKey === this.employeeStatusRecordKey(record);
    },

    editableStatusFields(record) {
      const source = record.source === "headcount" ? "headcount" : "periodic";
      const fields = source === "headcount" ? this.headcountStatusFields : this.periodicStatusFields;
      const optionMap = this.employeeStatusOptions[source] || {};
      return fields.map(field => {
        if (field.type !== "select" || field.options) {
          return field;
        }
        return {
          ...field,
          options: optionMap[field.key] || [],
        };
      });
    },

    fieldDraftValue(field, value) {
      if (field.type === "date") {
        return this.toDateInputValue(value);
      }
      if (field.type === "checkbox") {
        return Boolean(value);
      }
      return value ?? "";
    },

    normaliseDraftValue(field, value) {
      if (field.type === "date") {
        return value || "";
      }
      if (field.type === "number") {
        return value === "" || value === null || value === undefined ? "" : String(value);
      }
      if (field.type === "checkbox") {
        return Boolean(value);
      }
      return value ?? "";
    },

    openEmployeeStatusEditor(record) {
      this.employeeStatusEditingKey = this.employeeStatusRecordKey(record);
      this.employeeStatusDraft = {};
      for (const field of this.editableStatusFields(record)) {
        this.employeeStatusDraft[field.key] = this.fieldDraftValue(field, record[field.key]);
      }
      this.employeeStatusEditReason = "";
      this.employeeStatusSaveError = "";
    },

    closeEmployeeStatusEditor() {
      this.employeeStatusEditingKey = null;
      this.employeeStatusDraft = {};
      this.employeeStatusEditReason = "";
      this.employeeStatusSaveError = "";
      this.employeeStatusSaving = false;
    },

    buildEmployeeStatusChanges(record) {
      const changes = {};
      for (const field of this.editableStatusFields(record)) {
        const original = this.normaliseDraftValue(field, record[field.key]);
        const updated = this.normaliseDraftValue(field, this.employeeStatusDraft[field.key]);
        if (String(original) !== String(updated)) {
          changes[field.key] = field.type === "checkbox" ? Boolean(updated) : updated;
        }
      }
      return changes;
    },

    toDateInputValue(value) {
      if (!value) return "";
      const parsed = new Date(value);
      if (!Number.isNaN(parsed.getTime())) {
        return parsed.toISOString().split("T")[0];
      }
      const parts = String(value).trim().match(/^(\d{1,2})-([A-Za-z]{3})-(\d{4})$/);
      if (!parts) return "";
      const months = {
        Jan: "01", Feb: "02", Mar: "03", Apr: "04", May: "05", Jun: "06",
        Jul: "07", Aug: "08", Sep: "09", Oct: "10", Nov: "11", Dec: "12",
      };
      const month = months[parts[2]];
      if (!month) return "";
      return `${parts[3]}-${month}-${parts[1].padStart(2, "0")}`;
    },

    saveEmployeeStatus(record) {
      const changes = this.buildEmployeeStatusChanges(record);
      if (!Object.keys(changes).length) {
        this.employeeStatusSaveError = "No changes to save.";
        return;
      }
      if (!this.employeeStatusEditReason.trim()) {
        this.employeeStatusSaveError = "Please enter a reason for the change.";
        return;
      }

      this.employeeStatusSaving = true;
      this.employeeStatusSaveError = "";

      fetch(`/api/employee-status/${record.source}/${record.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json",
           "X-CSRFToken": csrfToken()
         },
        body: JSON.stringify({
          changes,
          reason: this.employeeStatusEditReason,
        }),
      })
        .then(r => r.json())
        .then(data => {
          this.employeeStatusSaving = false;
          if (data.error) {
            this.employeeStatusSaveError = data.error;
            return;
          }
          this.closeEmployeeStatusEditor();
          this.fetchEmployeeStatusOptions();
          this.fetchEmployeeStatus(this.activeStatusFilter);
          this.fetchMetrics();
          this.fetchNewHires();
        })
        .catch(err => {
          this.employeeStatusSaving = false;
          this.employeeStatusSaveError = err.message;
        });
    },

    formatDate(iso) {
      if (!iso) return "—";
      const d = new Date(iso);
      return d.toLocaleString("en-GB", {
        day: "2-digit", month: "short",
        hour: "2-digit", minute: "2-digit"
      });
    }
  };
}
