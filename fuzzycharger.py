import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# Δημιουργία ασαφών μεταβλητών για εισόδους και έξοδο
battery_level = ctrl.Antecedent(np.arange(0, 101, 1), 'battery_level')
energy_cost = ctrl.Antecedent(np.arange(0, 1.1, 0.1), 'energy_cost')
charging_rate = ctrl.Consequent(np.arange(0, 101, 1), 'charging_rate')

# Ορισμός των fuzzy sets για τις εισόδους και την έξοδο
battery_level['low'] = fuzz.trimf(battery_level.universe, [0, 0, 50])
battery_level['medium'] = fuzz.trimf(battery_level.universe, [30, 50, 80])
battery_level['high'] = fuzz.trimf(battery_level.universe, [60, 100, 100])

energy_cost['low'] = fuzz.trimf(energy_cost.universe, [0, 0, 0.5])
energy_cost['medium'] = fuzz.trimf(energy_cost.universe, [0.3, 0.5, 0.7])
energy_cost['high'] = fuzz.trimf(energy_cost.universe, [0.5, 1, 1])

charging_rate['slow'] = fuzz.trimf(charging_rate.universe, [0, 0, 50])
charging_rate['medium'] = fuzz.trimf(charging_rate.universe, [20, 50, 80])
charging_rate['fast'] = fuzz.trimf(charging_rate.universe, [60, 100, 100])

# Κανόνες ασαφούς λογικής
rule1 = ctrl.Rule(battery_level['low'] & energy_cost['low'], charging_rate['fast'])
rule2 = ctrl.Rule(battery_level['low'] & energy_cost['medium'], charging_rate['medium'])
rule3 = ctrl.Rule(battery_level['low'] & energy_cost['high'], charging_rate['slow'])
rule4 = ctrl.Rule(battery_level['medium'] & energy_cost['low'], charging_rate['medium'])
rule5 = ctrl.Rule(battery_level['medium'] & energy_cost['high'], charging_rate['slow'])
rule6 = ctrl.Rule(battery_level['high'], charging_rate['slow'])
rule7 = ctrl.Rule(battery_level['low'] & energy_cost['high'], charging_rate['slow'])  
rule8 = ctrl.Rule(battery_level['high'] & energy_cost['low'], charging_rate['medium'])  

# Δημιουργία συστήματος ελέγχου
charging_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8])
charging_simulation = ctrl.ControlSystemSimulation(charging_ctrl)

# Ιστορικό φορτίσεων
charging_history = []

# Συνάρτηση για τη φόρτιση
def simulate_charging(battery, cost, battery_type="standard"):
    efficiency_factor = 1
    if battery_type == "lithium":
        efficiency_factor = 0.85
    elif battery_type == "lead-acid":
        efficiency_factor = 0.75

    charging_simulation.input['battery_level'] = battery
    charging_simulation.input['energy_cost'] = cost

    charging_simulation.compute()
    charging = charging_simulation.output['charging_rate'] * efficiency_factor

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    charging_history.append((timestamp, battery, cost, charging))

    result = f"\n==== Αποτέλεσμα Προσομοίωσης Φόρτισης ====\n"
    result += f"Τύπος μπαταρίας: {battery_type.capitalize()}\n"
    result += f"Η μπαταρία σας είναι στο {battery}%. \n"

    if cost < 0.3:
        result += f"Το κόστος ενέργειας είναι χαμηλό ({cost}€/kWh). Η φόρτιση είναι οικονομική.\n"
    elif cost > 0.7:
        result += f"Το κόστος ενέργειας είναι υψηλό ({cost}€/kWh). Συνιστάται να αποφύγετε τη φόρτιση.\n"

    result += f"Προτεινόμενος ρυθμός φόρτισης: {charging:.2f}%\n"
    result += "===========================================\n"
    
    result += provide_alternatives(cost)
    return result

# Εναλλακτικές επιλογές
def provide_alternatives(cost):
    alternatives = "\n==== Εναλλακτικές Επιλογές ====\n"
    if cost < 0.3:
        alternatives += "Συνιστάται να φορτίσετε τώρα.\n"
    elif cost >= 0.3 and cost <= 0.7:
        alternatives += "Σκεφτείτε να περιμένετε αν είναι δυνατόν μέχρι το κόστος να μειωθεί.\n"
    else:
        alternatives += "Συνιστάται να αποφύγετε τη φόρτιση αυτή τη στιγμή.\n"
    alternatives += "===================================\n"
    return alternatives

# Ιστορικό
def display_charging_history():
    history = "\n==== Ιστορικό Φορτίσεων ====\n"
    for record in charging_history:
        history += f"{record[0]} | Επίπεδο Μπαταρίας: {record[1]}%, Κόστος: {record[2]}€/kWh, Ρυθμός Φόρτισης: {record[3]:.2f}%\n"
    history += "===================================\n"
    return history

# Οπτικοποίηση fuzzy sets
def visualize_fuzzy_sets():
    battery_level.view()
    energy_cost.view()
    charging_rate.view()
    plt.show()

# Έλεγχος έγκυρων τιμών
def validate_battery_cost(battery, cost):
    if not (0 <= battery <= 100):
        messagebox.showerror("Σφάλμα", "Το επίπεδο της μπαταρίας πρέπει να είναι μεταξύ 0% και 100%.")
        return False
    if not (0 <= cost <= 1):
        messagebox.showerror("Σφάλμα", "Το κόστος ενέργειας πρέπει να είναι μεταξύ 0 και 1 €/kWh.")
        return False
    return True

# GUI
def run_gui():
    def on_submit():
        try:
            battery = float(battery_entry.get())
            cost = float(cost_entry.get())
            battery_type = battery_type_entry.get().lower()

            if battery_type not in ["standard", "lithium", "lead-acid"]:
                messagebox.showerror("Σφάλμα", "Μη έγκυρος τύπος μπαταρίας.")
                return

            if not validate_battery_cost(battery, cost):
                return

            result = simulate_charging(battery, cost, battery_type)
            history = display_charging_history()

            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, result + history)

        except ValueError:
            messagebox.showerror("Σφάλμα", "Καταχωρήστε έγκυρες αριθμητικές τιμές.")

    def on_visualize():
        visualize_fuzzy_sets()

    root = tk.Tk()
    root.title("Σύστημα Φόρτισης Ηλεκτρικών Οχημάτων")

    # Προσαρμογή της διάταξης των στοιχείων
    root.grid_columnconfigure(1, weight=1)
    root.grid_rowconfigure(4, weight=1)

    tk.Label(root, text="Επίπεδο Μπαταρίας (%):").grid(row=0, column=0, sticky="e", padx=10, pady=5)
    tk.Label(root, text="Κόστος Ενέργειας (€/kWh):").grid(row=1, column=0, sticky="e", padx=10, pady=5)
    tk.Label(root, text="Τύπος Μπαταρίας(standard,lithium,lead-acid):").grid(row=2, column=0, sticky="e", padx=10, pady=5)

    battery_entry = tk.Entry(root)
    cost_entry = tk.Entry(root)
    battery_type_entry = tk.Entry(root)

    battery_entry.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
    cost_entry.grid(row=1, column=1, sticky="ew", padx=10, pady=5)
    battery_type_entry.grid(row=2, column=1, sticky="ew", padx=10, pady=5)

    submit_button = tk.Button(root, text="Υποβολή", command=on_submit)
    submit_button.grid(row=3, column=1, sticky="ew", padx=10, pady=5)

    visualize_button = tk.Button(root, text="Οπτικοποίηση", command=on_visualize)
    visualize_button.grid(row=3, column=0, sticky="ew", padx=10, pady=5)

    result_text = tk.Text(root, height=15, width=50)
    result_text.grid(row=4, columnspan=2, sticky="nsew", padx=10, pady=5)

    root.mainloop()

# Εκκίνηση της GUI
run_gui()
