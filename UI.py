import tkinter as tk
from tkinter import filedialog, messagebox
import pickle
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from processamento import *

global_my_list = []  # Variável global para armazenar my_list
station_checkbuttons = {}  # Dicionário para armazenar os estados dos checkboxes
station_vars = {}  # Dicionário para os estados das estações
global_columns = []  # Variável global para armazenar as colunas disponíveis para plotagem
current_figures = []  # Lista para armazenar figuras atuais para comparação

def select_file():
    """
    Função para abrir a janela de seleção de arquivo e carregar os dados.
    """
    global global_my_list, global_columns

    file_path = filedialog.askopenfilename(
        initialdir="Resultados",
        initialfile="selected_stations_just_events.pkl",
        title="Selecione um arquivo",
        filetypes=[("Pickle Files", "*.pkl"), ("Todos os arquivos", "*.*")]
    )

    if file_path:
        metadata, my_list = load_data(file_path)
        if metadata is not None and my_list is not None:
            global_my_list = my_list  # Armazena my_list na variável global
            print("Metadata:", metadata)
            print("My List:", my_list)

            # Preenchendo os checkboxes de estações na UI
            for widget in station_frame.winfo_children():
                widget.destroy()

            unique_stations = sorted(set(event['Estacao'] for event in my_list if 'Estacao' in event))
            for station in unique_stations:
                var = tk.BooleanVar()
                station_vars[station] = var
                cb = tk.Checkbutton(station_frame, text=station, variable=var, command=update_dates)
                cb.pack(anchor="w")

            # Coletando colunas disponíveis para plotagem
            if len(my_list) > 0 and 'Dados' in my_list[0] and not my_list[0]['Dados'].empty:
                global_columns = list(my_list[0]['Dados'].columns)
                field_combobox['values'] = global_columns
                if global_columns:
                    field_combobox.current(0)  # Seleciona a primeira coluna por padrão
        else:
            messagebox.showerror("Erro", "Não foi possível carregar os dados do arquivo.")

def update_dates():
    """
    Atualiza o combobox de datas com base nas estações selecionadas.
    Exibe apenas as datas que estão presentes em todas as estações selecionadas.
    """
    global global_my_list

    selected_stations = [station for station, var in station_vars.items() if var.get()]
    date_combobox['values'] = []  # Limpa o combobox

    if not selected_stations:
        return

    # Conjuntos de datas para cada estação selecionada
    station_date_sets = []
    for station in selected_stations:
        dates = set(event['DataHora'] for event in global_my_list if event['Estacao'] == station and 'DataHora' in event)
        station_date_sets.append(dates)

    # Interseção de todas as datas
    common_dates = set.intersection(*station_date_sets)

    date_combobox['values'] = [date.strftime("%Y-%m-%d %H:%M") for date in sorted(common_dates)]
    if date_combobox['values']:
        date_combobox.current(0)  # Seleciona a primeira data por padrão

def plot_graph(event, compare=False):
    """
    Plota o gráfico com base na data e no campo selecionados.
    """
    global global_my_list, current_figures
    selected_date = date_combobox.get()
    selected_field = field_combobox.get()

    selected_stations = [station for station, var in station_vars.items() if var.get()]

    if not selected_stations:
        messagebox.showinfo("Informação", "Nenhuma estação selecionada para plotagem.")
        return

    if not selected_field:
        messagebox.showinfo("Informação", "Nenhum campo selecionado para plotagem.")
        return

    fig, ax = plt.subplots(figsize=(6, 5))

    for station in selected_stations:
        for event in global_my_list:
            if event['Estacao'] == station and event['DataHora'].strftime("%Y-%m-%d %H:%M") == selected_date:
                if 'Dados' in event:
                    data = event['Dados']
                    if selected_field in data.columns:
                        ax.plot(data['TIME'], data[selected_field], label=f"{station}")

    ax.set_xlabel("Tempo (minutos)")
    ax.set_ylabel(selected_field)
    ax.set_title(f"{selected_field} - Data: {selected_date}")
    ax.legend()
    ax.grid(True)

    # Se for uma comparação, mantenha a figura existente
    if not compare:
        for widget in plot_frame.winfo_children():
            widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=plot_frame if not compare else tk.Toplevel(root))
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=False, padx=5, pady=5)

    if not compare:
        current_figures.append(fig)

    plt.tight_layout()
    plt.close(fig)

def compare_plot():
    """
    Compara o gráfico atual com um novo.
    """
    plot_graph(None, compare=True)

# Criando a interface gráfica
root = tk.Tk()
root.title("Carregador de Dados")

# Tamanho fixo da janela
root.geometry("1000x600")

# Frame principal
main_frame = tk.Frame(root)
main_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

# Frame para o gráfico
plot_frame = tk.Frame(root, width=400, height=300, bg="white")
plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Rótulo
label = tk.Label(main_frame, text="Clique no botão para carregar os dados.")
label.pack(pady=20)

# Botão para selecionar o arquivo
load_button = tk.Button(main_frame, text="Carregar Arquivo", command=select_file)
load_button.pack(pady=20)

# Frame para os checkboxes das estações
station_label = tk.Label(main_frame, text="Selecione as estações:")
station_label.pack(pady=10)
station_frame = tk.Frame(main_frame)
station_frame.pack(pady=10, fill=tk.BOTH, expand=True)

# Combobox para exibir as datas dos eventos
date_label = tk.Label(main_frame, text="Datas dos eventos:")
date_label.pack(pady=10)
date_combobox = ttk.Combobox(main_frame, state="readonly")
date_combobox.pack(pady=10)
date_combobox.bind("<<ComboboxSelected>>", plot_graph)

# Combobox para selecionar o campo para plotagem
field_label = tk.Label(main_frame, text="Selecione o campo para plotagem:")
field_label.pack(pady=10)
field_combobox = ttk.Combobox(main_frame, state="readonly")
field_combobox.pack(pady=10)
field_combobox.bind("<<ComboboxSelected>>", plot_graph)

# Botão para comparar gráficos
compare_button = tk.Button(main_frame, text="Comparar com Novo Gráfico", command=compare_plot)
compare_button.pack(pady=20)

# Rodar a aplicação
root.mainloop()
