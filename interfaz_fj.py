import tkinter as tk
from tkinter import ttk, messagebox
import os

# Importamos la lógica de negocio orientada a objetos que creamos previamente
from sistema_fj import (
    Cliente, ReservaDeSala, AlquilerDeEquipo, AsesoriaEspecializada,
    Reserva, SistemaException, ValidacionError
)

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Software FJ - Gestión Integral")
        self.geometry("600x550")
        
        # Datos en memoria (simulando la base de datos a través de listas)
        self.clientes = []
        
        # Instanciar servicios
        self.servicios = [
            ReservaDeSala("S01", "Sala Conferencias A", 100, capacidad=50),
            AlquilerDeEquipo("E01", "Laptop Dell XPS", 50, requiere_deposito=True),
            AsesoriaEspecializada("A01", "Consultoría en Ciberseguridad", 300, "Seguridad IT")
        ]
        self.reservas = []

        # Crear Notebook (Pestañas clásicas de ttk)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Frames para cada pestaña
        self.tab_cliente = ttk.Frame(self.notebook)
        self.tab_reserva = ttk.Frame(self.notebook)
        self.tab_cancelar = ttk.Frame(self.notebook)
        self.tab_logs = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_cliente, text="Registrar Cliente")
        self.notebook.add(self.tab_reserva, text="Nueva Reserva")
        self.notebook.add(self.tab_cancelar, text="Gestionar Reservas")
        self.notebook.add(self.tab_logs, text="Ver Logs")

        self.setup_tab_cliente()
        self.setup_tab_reserva()
        self.setup_tab_cancelar()
        self.setup_tab_logs()

    def setup_tab_cliente(self):
        tk.Label(self.tab_cliente, text="Alta de Nuevo Cliente", font=("Arial", 16, "bold")).pack(pady=15)

        frame_form = tk.Frame(self.tab_cliente)
        frame_form.pack(pady=10)

        tk.Label(frame_form, text="ID Cliente:").grid(row=0, column=0, sticky='e', pady=5, padx=5)
        self.entry_id_cliente = tk.Entry(frame_form, width=30)
        self.entry_id_cliente.grid(row=0, column=1, pady=5)

        tk.Label(frame_form, text="Nombre:").grid(row=1, column=0, sticky='e', pady=5, padx=5)
        self.entry_nombre = tk.Entry(frame_form, width=30)
        self.entry_nombre.grid(row=1, column=1, pady=5)

        tk.Label(frame_form, text="Correo:").grid(row=2, column=0, sticky='e', pady=5, padx=5)
        self.entry_correo = tk.Entry(frame_form, width=30)
        self.entry_correo.grid(row=2, column=1, pady=5)

        tk.Label(frame_form, text="Teléfono:").grid(row=3, column=0, sticky='e', pady=5, padx=5)
        self.entry_telefono = tk.Entry(frame_form, width=30)
        self.entry_telefono.grid(row=3, column=1, pady=5)

        tk.Button(self.tab_cliente, text="Registrar Cliente", command=self.registrar_cliente, width=20).pack(pady=20)

    def registrar_cliente(self):
        try:
            id_cliente = self.entry_id_cliente.get()
            nombre = self.entry_nombre.get()
            correo = self.entry_correo.get()
            telefono = self.entry_telefono.get()
            
            if not id_cliente:
                raise ValidacionError("El ID del cliente es obligatorio.")

            # Instanciar cliente, validaciones se ejecutan
            nuevo_cliente = Cliente(id_cliente, nombre, correo, telefono)
            self.clientes.append(nuevo_cliente)
            
            self.actualizar_dropdown_clientes()
            messagebox.showinfo("Éxito", f"Cliente {nuevo_cliente.nombre} registrado correctamente.")
            
            # Limpiar
            self.entry_id_cliente.delete(0, 'end')
            self.entry_nombre.delete(0, 'end')
            self.entry_correo.delete(0, 'end')
            self.entry_telefono.delete(0, 'end')
            
            self.log_internal(f"Cliente registrado: {nuevo_cliente.nombre}")
        except Exception as e:
            messagebox.showerror("Error de Registro", str(e))

    def setup_tab_reserva(self):
        tk.Label(self.tab_reserva, text="Procesamiento de Reservas", font=("Arial", 16, "bold")).pack(pady=15)

        frame_form = tk.Frame(self.tab_reserva)
        frame_form.pack(pady=10)

        # Selección de Cliente
        tk.Label(frame_form, text="Seleccione Cliente:").grid(row=0, column=0, sticky='e', pady=10, padx=5)
        self.combo_clientes = ttk.Combobox(frame_form, width=27, state="readonly")
        self.combo_clientes.grid(row=0, column=1, pady=10)

        # Selección de Servicio
        tk.Label(frame_form, text="Seleccione Servicio:").grid(row=1, column=0, sticky='e', pady=10, padx=5)
        nombres_servicios = [s.nombre for s in self.servicios]
        self.combo_servicios = ttk.Combobox(frame_form, values=nombres_servicios, width=27, state="readonly")
        self.combo_servicios.grid(row=1, column=1, pady=10)
        self.combo_servicios.bind("<<ComboboxSelected>>", self.actualizar_parametros_servicio)
        
        self.btn_disponibilidad = tk.Button(frame_form, text="Hacer (In)disponible", command=self.alternar_disponibilidad_servicio)
        self.btn_disponibilidad.grid(row=1, column=2, padx=5)
        
        # Parámetros variables
        self.label_param1 = tk.Label(frame_form, text="Parámetro:")
        self.label_param1.grid(row=2, column=0, sticky='e', pady=10, padx=5)
        self.entry_param1 = tk.Entry(frame_form, width=30)
        self.entry_param1.grid(row=2, column=1, pady=10)

        self.var_opcional = tk.IntVar()
        self.check_opcional = tk.Checkbutton(frame_form, text="Opcional", variable=self.var_opcional)
        self.check_opcional.grid(row=3, column=1, sticky='w', pady=10)

        tk.Button(self.tab_reserva, text="Procesar y Confirmar Reserva", command=self.procesar_reserva, width=30).pack(pady=20)

        # Iniciar estado UI
        if nombres_servicios:
            self.combo_servicios.current(0)
            self.actualizar_parametros_servicio(None)

    def alternar_disponibilidad_servicio(self):
        servicio_str = self.combo_servicios.get()
        servicio_obj = next((s for s in self.servicios if s.nombre == servicio_str), None)
        if servicio_obj:
            nuevo_estado = not servicio_obj.disponible
            servicio_obj.modificar_disponibilidad(nuevo_estado)
            estado = "DISPONIBLE" if nuevo_estado else "NO DISPONIBLE"
            messagebox.showinfo("Estado de Servicio", f"El servicio '{servicio_obj.nombre}' ahora está: {estado}")
            self.log_internal(f"Disponibilidad de {servicio_obj.nombre} cambiada a {estado}")

    def actualizar_dropdown_clientes(self):
        nombres = [f"{c.nombre} ({c.id_entidad})" for c in self.clientes]
        self.combo_clientes['values'] = nombres
        if nombres:
            self.combo_clientes.current(len(nombres)-1)

    def actualizar_parametros_servicio(self, event):
        choice = self.combo_servicios.get()
        if "Sala" in choice:
            self.label_param1.config(text="Duración (Horas):")
            self.check_opcional.config(text="Incluir Proyector")
        elif "Laptop" in choice or "Equipo" in choice:
            self.label_param1.config(text="Tiempo (Días):")
            self.check_opcional.config(text="Seguro Adicional")
        else:
            self.label_param1.config(text="Cantidad de Sesiones:")
            self.check_opcional.config(text="Modalidad de Urgencia")
        self.var_opcional.set(0)

    def procesar_reserva(self):
        cliente_str = self.combo_clientes.get()
        servicio_str = self.combo_servicios.get()
        param_val = self.entry_param1.get()
        opcional_val = bool(self.var_opcional.get())

        if not self.clientes:
            messagebox.showerror("Error", "Debes registrar al menos un cliente primero.")
            return

        cliente_obj = next((c for c in self.clientes if c.id_entidad in cliente_str), None)
        servicio_obj = next((s for s in self.servicios if s.nombre == servicio_str), None)

        if not cliente_obj or not servicio_obj:
            messagebox.showerror("Error", "Seleccione un cliente y un servicio válidos.")
            return

        try:
            try:
                param_num = int(param_val) if param_val.isdigit() else float(param_val)
            except ValueError:
                raise ValidacionError("El parámetro debe ser un valor numérico.")

            kwargs = {}
            if isinstance(servicio_obj, ReservaDeSala):
                kwargs = {'horas': param_num, 'incluye_proyector': opcional_val}
            elif isinstance(servicio_obj, AlquilerDeEquipo):
                kwargs = {'dias': int(param_num), 'seguro_adicional': opcional_val}
            elif isinstance(servicio_obj, AsesoriaEspecializada):
                kwargs = {'sesiones': int(param_num), 'modalidad_urgente': opcional_val}

            id_reserva = f"R{len(self.reservas)+1:03d}"
            nueva_reserva = Reserva(id_reserva, cliente_obj, servicio_obj, kwargs)
            
            nueva_reserva.procesar_reserva()
            self.reservas.append(nueva_reserva)
            
            messagebox.showinfo("Reserva Exitosa", f"¡Reserva {id_reserva} Confirmada!\nTotal a pagar: ${nueva_reserva.costo_total}")
            self.log_internal(f"Reserva exitosa: {id_reserva} | Total: ${nueva_reserva.costo_total} | {servicio_obj.nombre}")
            self.actualizar_dropdown_reservas()
            
        except ValidacionError as e:
            messagebox.showerror("Error de Validación", str(e))
            self.log_internal(f"Fallo en validación: {e}")
        except SistemaException as e:
            messagebox.showerror("Error del Sistema", str(e))
            self.log_internal(f"Error en el sistema: {e}")
        except Exception as e:
            messagebox.showerror("Error Crítico", str(e))
            self.log_internal(f"Fallo crítico: {e}")

    def setup_tab_cancelar(self):
        tk.Label(self.tab_cancelar, text="Cancelar Reservas Existentes", font=("Arial", 16, "bold")).pack(pady=15)

        frame_form = tk.Frame(self.tab_cancelar)
        frame_form.pack(pady=10)

        tk.Label(frame_form, text="Seleccione Reserva:").grid(row=0, column=0, sticky='e', pady=10, padx=5)
        self.combo_reservas = ttk.Combobox(frame_form, width=40, state="readonly")
        self.combo_reservas.grid(row=0, column=1, pady=10)

        tk.Button(self.tab_cancelar, text="Cancelar Reserva Seleccionada", command=self.cancelar_reserva, width=30).pack(pady=20)

    def actualizar_dropdown_reservas(self):
        lista = [f"{r.id_reserva} - {r.cliente.nombre} - {r.estado}" for r in self.reservas]
        self.combo_reservas['values'] = lista
        if lista:
            self.combo_reservas.current(len(lista)-1)
        else:
            self.combo_reservas.set('')

    def cancelar_reserva(self):
        reserva_str = self.combo_reservas.get()
        if not reserva_str:
            messagebox.showerror("Error", "No hay reservas seleccionadas.")
            return
            
        id_reserva = reserva_str.split(" - ")[0]
        reserva_obj = next((r for r in self.reservas if r.id_reserva == id_reserva), None)
        
        if not reserva_obj:
            messagebox.showerror("Error", "No se encontró la reserva internamente.")
            return
            
        try:
            reserva_obj.cancelar_reserva()
            messagebox.showinfo("Éxito", f"La reserva {id_reserva} ha sido cancelada satisfactoriamente.")
            self.log_internal(f"Reserva {id_reserva} cancelada.")
            self.actualizar_dropdown_reservas()
        except SistemaException as e:
            messagebox.showerror("Error de Operación", str(e))
            self.log_internal(f"Error al cancelar {id_reserva}: {e}")

    def setup_tab_logs(self):
        tk.Label(self.tab_logs, text="Auditoría y Registros del Sistema", font=("Arial", 16, "bold")).pack(pady=10)

        # Text box con scrollbar
        frame_text = tk.Frame(self.tab_logs)
        frame_text.pack(padx=10, pady=10, fill="both", expand=True)

        scrollbar = tk.Scrollbar(frame_text)
        scrollbar.pack(side="right", fill="y")

        self.textbox_logs = tk.Text(frame_text, width=70, height=18, yscrollcommand=scrollbar.set)
        self.textbox_logs.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.textbox_logs.yview)

        self.textbox_logs.insert("1.0", "[SISTEMA] Interfaz gráfica (básica) iniciada.\n")
        self.textbox_logs.config(state="disabled")

        tk.Button(self.tab_logs, text="Cargar Logs desde 'software_fj_logs.txt'", command=self.cargar_archivo_logs, width=40).pack(pady=10)

    def log_internal(self, msg):
        self.textbox_logs.config(state="normal")
        self.textbox_logs.insert("end", f"> {msg}\n")
        self.textbox_logs.config(state="disabled")
        self.textbox_logs.see("end")

    def cargar_archivo_logs(self):
        try:
            if os.path.exists("software_fj_logs.txt"):
                with open("software_fj_logs.txt", "r") as f:
                    contenido = f.read()
                self.textbox_logs.config(state="normal")
                self.textbox_logs.insert("end", "\n" + "="*45 + "\n")
                self.textbox_logs.insert("end", "LECTURA DE ARCHIVO: software_fj_logs.txt\n")
                self.textbox_logs.insert("end", "="*45 + "\n")
                self.textbox_logs.insert("end", contenido)
                self.textbox_logs.config(state="disabled")
                self.textbox_logs.see("end")
            else:
                self.log_internal("Error: No se encontró el archivo de logs 'software_fj_logs.txt'.")
        except Exception as e:
            self.log_internal(f"Fallo al intentar leer logs: {e}")

if __name__ == "__main__":
    app = App()
    app.mainloop()
