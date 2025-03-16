import customtkinter as ctk
import pulp
from tkinter import messagebox
from tkinter import ttk


class ShiftSchedulerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Shift Scheduler")
        self.geometry("700x500")

        self.shifts = []  # List of tuples (shift_name, required_staff, shift_duration)
        self.staff = {}  # Dictionary of {name: {min_hours, max_hours, wage}}

        self.create_widgets()

    def create_widgets(self):
        # Section to enter shifts
        self.shift_label = ctk.CTkLabel(self, text="Enter Shift, Required Staff and Duration")
        self.shift_label.pack()

        self.shift_entry = ctk.CTkEntry(self, placeholder_text="Shift Name")
        self.shift_entry.pack()

        self.staff_required_entry = ctk.CTkEntry(self, placeholder_text="Required Staff")
        self.staff_required_entry.pack()

        self.shift_duration_entry = ctk.CTkEntry(self, placeholder_text="Shift Duration (Hours)")
        self.shift_duration_entry.pack()

        self.add_shift_btn = ctk.CTkButton(self, text="Add Shift", command=self.add_shift)
        self.add_shift_btn.pack()

        # Table for displaying shift data
        self.shift_table_label = ctk.CTkLabel(self, text="Shift Table")
        self.shift_table_label.pack()

        self.shift_table = ttk.Treeview(self, columns=("Shift Name", "Required Staff", "Duration (hrs)"),
                                        show="headings")
        self.shift_table.heading("Shift Name", text="Shift Name")
        self.shift_table.heading("Required Staff", text="Required Staff")
        self.shift_table.heading("Duration (hrs)", text="Duration (hrs)")

        self.shift_table.pack()

        # Section to enter staff details
        self.staff_label = ctk.CTkLabel(self, text="Enter Staff Details")
        self.staff_label.pack()

        self.staff_name_entry = ctk.CTkEntry(self, placeholder_text="Staff Name")
        self.staff_name_entry.pack()

        self.min_hours_entry = ctk.CTkEntry(self, placeholder_text="Min Hours")
        self.min_hours_entry.pack()

        self.max_hours_entry = ctk.CTkEntry(self, placeholder_text="Max Hours")
        self.max_hours_entry.pack()

        self.wage_entry = ctk.CTkEntry(self, placeholder_text="Hourly Wage")
        self.wage_entry.pack()

        self.add_staff_btn = ctk.CTkButton(self, text="Add Staff", command=self.add_staff)
        self.add_staff_btn.pack()

        self.staff_listbox = ctk.CTkTextbox(self, height=100)
        self.staff_listbox.pack()

        # Generate schedule button
        self.generate_btn = ctk.CTkButton(self, text="Generate Schedule", command=self.generate_schedule)
        self.generate_btn.pack()

    def add_shift(self):
        shift_name = self.shift_entry.get()
        try:
            required_staff = int(self.staff_required_entry.get())
            shift_duration = int(self.shift_duration_entry.get())
            self.shifts.append((shift_name, required_staff, shift_duration))

            # Insert into the Treeview table
            self.shift_table.insert('', 'end', values=(shift_name, required_staff, shift_duration))

        except ValueError:
            messagebox.showerror("Error", "Enter valid numbers for required staff and shift duration")

    def add_staff(self):
        name = self.staff_name_entry.get()
        try:
            min_hours = int(self.min_hours_entry.get())
            max_hours = int(self.max_hours_entry.get())
            wage = float(self.wage_entry.get())
            self.staff[name] = {"min": min_hours, "max": max_hours, "wage": wage}
            self.staff_listbox.insert('end', f"{name} - Min: {min_hours}, Max: {max_hours}, Wage: {wage}\n")
        except ValueError:
            messagebox.showerror("Error", "Enter valid numbers for hours and wage")

    def generate_schedule(self):
        if not self.shifts or not self.staff:
            messagebox.showerror("Error", "Enter shifts and staff first")
            return

        # Define the optimisation problem
        prob = pulp.LpProblem("ShiftScheduling", pulp.LpMinimize)

        # Decision variables
        schedule_vars = {}
        for shift, _, _ in self.shifts:
            for staff in self.staff:
                schedule_vars[(staff, shift)] = pulp.LpVariable(f"{staff}_{shift}", 0, 1, pulp.LpBinary)

        # Objective: Minimize total wage cost
        prob += pulp.lpSum(schedule_vars[(s, sh)] * self.staff[s]["wage"] for s, sh in schedule_vars)

        # Constraints
        for shift, required, _ in self.shifts:
            prob += pulp.lpSum(schedule_vars[(s, shift)] for s in self.staff) == required

        for staff in self.staff:
            hours_assigned = pulp.lpSum(schedule_vars[(staff, sh)] for sh, _, _ in self.shifts)
            prob += hours_assigned >= self.staff[staff]["min"]
            prob += hours_assigned <= self.staff[staff]["max"]

        # Solve the problem
        prob.solve()

        # Display results
        results = "Generated Schedule:\n"
        total_cost = 0
        staff_hours = {s: 0 for s in self.staff}
        staff_earnings = {s: 0 for s in self.staff}

        for (staff, shift), var in schedule_vars.items():
            if pulp.value(var) == 1:
                results += f"{staff} is assigned to {shift}\n"
                staff_hours[staff] += 1
                staff_earnings[staff] += self.staff[staff]["wage"]
                total_cost += self.staff[staff]["wage"]

        results += "\nEmployee Hours and Earnings:\n"
        for staff in self.staff:
            results += f"{staff}: {staff_hours[staff]} hours, £{staff_earnings[staff]:.2f}\n"

        results += f"\nTotal Payroll Cost: £{total_cost:.2f}"

        messagebox.showinfo("Schedule", results)


if __name__ == "__main__":
    app = ShiftSchedulerApp()
    app.mainloop()
