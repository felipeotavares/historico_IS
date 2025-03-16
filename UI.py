import tkinter as tk
from tkinter import filedialog, messagebox
import pickle
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
# from processamento import *

global_my_list = []  # Variável global para armazenar my_list
station_checkbuttons = {}  # Dicionário para armazenar os estados dos checkboxes
station_vars = {}  # Dicionário para os estados das estações
global_columns = []  # Variável global para armazenar as colunas disponíveis para plotagem
global_columns_Fft = []  # Variável global para armazenar as colunas disponíveis para plotagem
current_figures = []  # Lista para armazenar figuras atuais para comparação

# def load_data(file_path):
#     # Carregando os metadados e a lista do arquivo
#     with open(file_path, 'rb') as file:
#         # Lê os metadados até o delimitador
#         metadata = ""
#         for line in file:
#             if line.strip() == b'===END_METADATA===':
#                 break
#             metadata += line.decode('utf-8')

#         # Carrega a lista serializada
#         data_list = pickle.load(file)
    
#     return metadata, data_list 

def load_data(file_path):
    """
    Carrega os dados do arquivo e atualiza a barra de progresso.
    """
    # Criar uma nova janela para a barra de progresso
    progress_window = tk.Toplevel(root)
    progress_window.title("Carregando Dados")
    progress_label = tk.Label(progress_window, text="Carregando dados...")
    progress_label.pack(pady=10)
    
    progress_bar = ttk.Progressbar(progress_window, orient="horizontal", mode="determinate")
    progress_bar.pack(pady=10, padx=20, fill=tk.X)

    # Determinar o número total de linhas no arquivo
    total_lines = sum(1 for _ in open(file_path, 'rb'))
    progress_bar["maximum"] = total_lines
    
    # Carregar metadados e a lista serializada
    metadata = ""
    data_list = None
    with open(file_path, 'rb') as file:
        for i, line in enumerate(file):
            # Atualizar a barra de progresso
            progress_bar["value"] = i + 1
            progress_window.update()  # Atualiza a interface gráfica
            
            if line.strip() == b'===END_METADATA===':
                break
            metadata += line.decode('utf-8')
        
        # Carregar o restante do arquivo como objeto pickle
        data_list = pickle.load(file)
    
    # Fechar a janela de progresso após o carregamento
    progress_window.destroy()
    return metadata, data_list

def select_file():
    """
    Função para abrir a janela de seleção de arquivo e carregar os dados.
    """
    global global_my_list, global_columns, global_columns_fft

    file_path = filedialog.askopenfilename(
        initialdir="Resultados",
        initialfile="selected_stations_eventwindow_2h.pkl",
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
            row, col = 0, 0  # Inicializando linha e coluna
            for i, station in enumerate(unique_stations):
                var = tk.BooleanVar()
                station_vars[station] = var
                # cb = tk.Checkbutton(station_frame, text=station, variable=var, command=update_dates)
                cb = tk.Checkbutton(
                    station_frame, 
                    text=station, 
                    variable=var, 
                    command=lambda: [update_dates(), draw_graphs(None)]
                )
                cb.grid(row=row, column=col, padx=5, pady=5, sticky="w")  # Organizando em grade
            
                # Incrementando para próxima posição
                col += 1
                if col >= 4:  # Define 4 colunas por linha, por exemplo
                    col = 0
                    row += 1

            # Coletando colunas disponíveis para plotagem
            if len(my_list) > 0 and 'Dados' in my_list[0] and not my_list[0]['Dados'].empty:
                global_columns = list(my_list[0]['Dados'].columns)
                field_combobox['values'] = global_columns
                if global_columns:
                    field_combobox.current(3)  # Seleciona a 3 coluna por padrão
            # Coletando colunas disponíveis para plotagem
            if len(my_list) > 0 and 'FFT' in my_list[0] and not my_list[0]['FFT'].empty:
                global_columns_fft = list(my_list[0]['FFT'].columns)
                field_combobox_fft['values'] = global_columns_fft
                if global_columns_fft:
                    field_combobox_fft.current(1)  # Seleciona a primeira coluna por padrão
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
        
    # draw_graphs()

def plot_timeseries(event, compare=False):
    """
    Plota o gráfico com base na data e no campo selecionados.
    """
    global global_my_list, current_figures
    selected_date = date_combobox.get()
    selected_field = field_combobox.get()
    selected_field_fft = field_combobox_fft.get()

    selected_stations = [station for station, var in station_vars.items() if var.get()]

    if not selected_stations:
        messagebox.showinfo("Informação", "Nenhuma estação selecionada para plotagem.")
        return

    if not selected_field:
        messagebox.showinfo("Informação", "Nenhum campo selecionado para plotagem.")
        return

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6, 8))

    for station in selected_stations:
        for event in global_my_list:
            if event['Estacao'] == station and event['DataHora'].strftime("%Y-%m-%d %H:%M") == selected_date:
                if 'Dados' in event:
                    data = event['Dados']
                    if selected_field in data.columns:
                        ax1.plot(data['TIME'], data[selected_field], label=f"{station}")
                if 'FFT' in event:
                    fft_data = event['FFT']
                    if selected_field_fft in fft_data.columns:
                        ax2.plot(fft_data['Frequencia (mHz)'], fft_data[selected_field_fft], label=f"{station} - FFT")

    ax1.set_xlabel("Tempo (minutos)")
    ax1.set_ylabel(selected_field)
    ax1.set_title(f"{selected_field} - Data: {selected_date}")
    ax1.legend()
    ax1.grid(True)

    ax2.set_xlabel("Frequência (Hz)")
    ax2.set_ylabel(selected_field_fft)
    ax2.set_title(f"FFT: {selected_field_fft} - Data: {selected_date}")
    ax2.legend()
    ax2.grid(True)

    # Se for uma comparação, mantenha a figura existente
    if not compare:
        for widget in plot_frame.winfo_children():
            widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=plot_frame if not compare else tk.Toplevel(root))
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.Y, expand=False, padx=0, pady=0)

    if not compare:
        current_figures.append(fig)

    plt.tight_layout()
    plt.close(fig)

def compare_plot():
    """
    Compara o gráfico atual com um novo.
    """
    plot_timeseries(None, compare=True)

def show_selected_info(event):
    """
    Exibe todas as informações do evento selecionado em uma caixa de texto.
    """
    global global_my_list
    selected_date = date_combobox.get()

    selected_stations = [station for station, var in station_vars.items() if var.get()]

    if not selected_stations:
        return

    for event in global_my_list:
        if event['DataHora'].strftime("%Y-%m-%d %H:%M") == selected_date and event['Estacao'] in selected_stations:
            info_textbox.delete(1.0, tk.END)
            for key, value in event.items():
                if not key == 'Dados' and not key== 'FFT':
                    info_textbox.insert(tk.END, f"{key}: {value}\n")
            break

def draw_graphs(event):
    """
    Função chamada ao selecionar um campo no combobox.
    Pode executar múltiplas ações.
    """
    plot_timeseries(event)  # Função já existente para plotar o gráfico
    show_selected_info(event)
    

# Criando a interface gráfica
root = tk.Tk()
root.title("Carregador de Dados")

# Tamanho fixo da janela
root.geometry("1200x800")

# Frame principal
main_frame = tk.Frame(root)
main_frame.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)

# Frame para o gráfico
plot_frame = tk.Frame(root, width=100, height=100, bg="white")
plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Rótulo
# label = tk.Label(main_frame, text="Clique no botão para carregar os dados.")
# label.pack(pady=20)

# Botão para selecionar o arquivo
load_button = tk.Button(main_frame, text="Carregar Arquivo", command=select_file)
load_button.pack(pady=5)

# Frame para os checkboxes das estações
station_label = tk.Label(main_frame, text="Selecione as estações:")
station_label.pack(pady=5)
station_frame = tk.Frame(main_frame)
station_frame.pack(pady=5, fill=tk.BOTH, expand=True)

# Combobox para exibir as datas dos eventos
date_label = tk.Label(main_frame, text="Datas dos eventos:")
date_label.pack(pady=5)
date_combobox = ttk.Combobox(main_frame, state="readonly")
date_combobox.pack(pady=5)
date_combobox.bind("<<ComboboxSelected>>", draw_graphs)

# Combobox para selecionar o campo para plotagem
field_label = tk.Label(main_frame, text="Selecione o campo para plotagem:")
field_label.pack(pady=5)
field_combobox = ttk.Combobox(main_frame, state="readonly")
field_combobox.pack(pady=5)
field_combobox.bind("<<ComboboxSelected>>", draw_graphs)

# Combobox para selecionar o campo FFT para plotagem
field_label_fft = tk.Label(main_frame, text="Selecione o campo FFT:")
field_label_fft.pack(pady=5)
field_combobox_fft = ttk.Combobox(main_frame, state="readonly")
field_combobox_fft.pack(pady=5)
field_combobox_fft.bind("<<ComboboxSelected>>", draw_graphs)

# Textbox para exibir informações detalhadas do evento selecionado
info_label = tk.Label(main_frame, text="Informações do Evento:")
info_label.pack(pady=5)
info_textbox = tk.Text(main_frame, height=10, width=30)
info_textbox.pack(pady=5)

# Botão para comparar gráficos
compare_button = tk.Button(main_frame, text="Comparar com Novo Gráfico", command=compare_plot)
compare_button.pack(pady=5)

# Rodar a aplicação
root.mainloop()
