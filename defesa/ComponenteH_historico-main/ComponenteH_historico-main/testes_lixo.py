import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime, timedelta
from requests.packages.urllib3.exceptions import InsecureRequestWarning

def intermagnet_download(files_folder, date_str, station, duration):
    date = datetime.strptime(date_str, "%Y-%m-%d")
    d = date.strftime('%Y%m%d')
    url = "https://imag-data.bgs.ac.uk/GIN_V1/GINServices"
    params = {
        "Request": "GetData",
        "format": "Iaga2002",
        "testObsys": 0,
        "observatoryIagaCode": station,
        "samplesPerDay": "minute",
        "publicationState": "Best available",
        "dataStartDate": date_str,
        "dataDuration": duration
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.text
        save_folder = os.path.join(files_folder, 'Dados', d)
        file_name = f'{station.lower()}{d}vmin.min'
        full_save_path = os.path.join(save_folder, file_name)

        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        if os.path.exists(full_save_path):
            print(f"[{file_name}] Already on the disk")
        else:
            with open(full_save_path, "w") as file:
                file.write(data)
            print(f"[{file_name}] Downloaded")

        # Combine files if this is the first day
        if duration == 1 or date == datetime.strptime(date_str, "%Y-%m-%d"):
            combined_file_path = os.path.join(files_folder, file_name)
            with open(combined_file_path, 'w') as combined_file:
                combined_file.write(data)
        else:
            combined_file_path = os.path.join(files_folder, f'{station.lower()}{date_str.replace("-", "")}vmin.min')
            with open(combined_file_path, 'a') as combined_file:
                combined_file.write(data)
#%%
def download_embrace(files_folder, date_str, station, duration):
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    date = datetime.strptime(date_str, "%Y-%m-%d")
    combined_file_name = None

    for day_offset in range(duration):
        current_date = date + timedelta(days=day_offset)
        d = current_date.strftime('%Y%m%d')
        folder_save = os.path.join(files_folder, 'Dados', d)

        if not os.path.exists(folder_save):
            os.makedirs(folder_save)

        base_url = "https://embracedata.inpe.br/magnetometer/"
        variable_url = f"{station}/{current_date.year}/"
        final_url = urljoin(base_url, variable_url)

        response = requests.get(final_url, verify=False)
        if response.status_code != 200:
            print(f"Failed to access data for {current_date.strftime('%Y-%m-%d')}")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')

        for link in soup.find_all('a'):
            file_name = link.get('href')
            if file_name == "../" or not file_name.endswith(f'.{current_date.year % 100}m'):
                continue

            wanted_date = current_date.strftime("%d%b").lower()
            file_date = file_name[3:8]

            if wanted_date == file_date:
                local_file_path = os.path.join(folder_save, file_name)
                if os.path.exists(local_file_path):
                    print(f"[{file_name}] Already on the disk")
                else:
                    file_url = urljoin(final_url, file_name)
                    print(f"[{file_name}] Downloaded")
                    with open(local_file_path, 'wb') as file:
                        file_response = requests.get(file_url, verify=False)
                        file.write(file_response.content)

                if combined_file_name is None:
                    combined_file_name = file_name
                    combined_file_path = os.path.join(files_folder, combined_file_name)

                # Append the content to the combined file
                with open(combined_file_path, 'ab') as combined_file:
                    with open(local_file_path, 'rb') as file:
                        combined_file.write(file.read())

    if combined_file_name:
        print(f"Combined file saved at: {combined_file_path}")
    else:
        print("No files were downloaded.")

# Exemplo de uso:
download_embrace("", "2024-05-10", "SMS", 3)
intermagnet_download("", "2024-05-10", "ASC", 3)
intermagnet_download("", "2024-05-10", "KDU", 3)

#%%
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime, timedelta
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import pandas as pd
import numpy as np

def find_header(file_path):
    station_name = os.path.basename(file_path)[:3].upper()
    line_count, kind = 0, np.nan  # Inicializa kind com np.nan

    with open(file_path, 'r') as file:
        for line in file:
            if " Reported               HDZF" in line:
                kind = "HDZF"
            elif " Reported               XYZ" in line:
                kind = "XYZF"
            elif line.startswith('DATE') or line.startswith(' DD MM YYYY'):
                if line.startswith(' DD MM YYYY'):
                    kind = 'EMBRACE'
                break
            line_count += 1

    return station_name, line_count, kind

def process_data(file_path, start_date):
    try:
        # Tenta encontrar o cabeçalho e o tipo de arquivo
        try:
            station_name, header_lines, kind = find_header(file_path)
        except Exception as e:
            return None, None

        # Tenta ler o arquivo CSV
        try:
            df = pd.read_csv(file_path, skiprows=header_lines, sep='\s+')
        except pd.errors.EmptyDataError:
            return None, None
        except FileNotFoundError:
            return None, None
        except Exception as e:
            return None, None

        # Processamento de acordo com o tipo de arquivo identificado
        try:
            if kind == "HDZF" or kind == "XYZF":
                df['TIME'] = pd.to_datetime(df['DATE'] + ' ' + df['TIME'], errors='coerce')
                df['TIME'] = df['TIME'].dt.hour + df['TIME'].dt.minute / 60 + df['TIME'].dt.second / 3600
                df['DATETIME'] = pd.to_datetime(start_date) + pd.to_timedelta(df['TIME'], unit='h')

                if kind == "XYZF":
                    # Calcula a componente H
                    df[f'{station_name}H'] = np.sqrt(df[f'{station_name}X']**2 + df[f'{station_name}Y']**2)
                    df[f'{station_name}D'] = np.arctan2(df[f'{station_name}Y'], df[f'{station_name}X']) * (180 / np.pi) * 60  # converte de rad para arc min

                df[f'{station_name}H1'] = df[f'{station_name}H'] - df[f'{station_name}H'][0]
                df[f'{station_name}D1'] = df[f'{station_name}D'] - df[f'{station_name}D'][0]
                df['H_nT'] = np.where(df[f'{station_name}H'] > 99999, np.nan, df[f'{station_name}H1'])
                df['D_deg'] = np.where(df[f'{station_name}D'] > 99999, np.nan, df[f'{station_name}D1'] / 60)  # converte de arc min para deg

            elif kind == 'EMBRACE':
                df['DATE'] = pd.to_datetime(df['YYYY'].astype(str) + '-' + df['MM'].astype(str) + '-' + df['DD'].astype(str), errors='coerce')
                df['TIME'] = pd.to_timedelta(df['HH'], unit='h') + pd.to_timedelta(df['MM.1'], unit='m')
                df['DATETIME'] = df['DATE'] + df['TIME']
                df['TIME'] = df['DATETIME'].dt.hour + df['DATETIME'].dt.minute / 60 + df['DATETIME'].dt.second / 3600

                df[f'{station_name}H'] = df['H(nT)'] - df['H(nT)'][0]
                df[f'{station_name}D'] = df['D(Deg)'] - df['D(Deg)'][0]
                df['H_nT'] = np.where(df[f'{station_name}H'] > 99999, np.nan, df[f'{station_name}H'])
                df['D_deg'] = np.where(df[f'{station_name}D'] > 99999, np.nan, df[f'{station_name}D'])
            else:
                return None, None
        except KeyError as e:
            return None, None
        except Exception as e:
            return None, None

        # Tenta detectar anomalias e calcular a diferença
        try:
            df['dH_nT'] = df['H_nT'].diff()
            df['dD_deg'] = df['D_deg'].diff()
        except Exception as e:
            return None, None

        return df[['DATETIME', 'TIME', 'H_nT', 'dH_nT', 'D_deg', 'dD_deg']], station_name

    except Exception as e:
        return None, None

def download_embrace(files_folder, date_str, station, duration):
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    date = datetime.strptime(date_str, "%Y-%m-%d")
    combined_file_name = None

    half_duration = (duration - 1) // 2
    start_date = date - timedelta(days=half_duration)
    end_date = date + timedelta(days=half_duration)

    for day_offset in range((end_date - start_date).days + 1):
        current_date = start_date + timedelta(days=day_offset)
        d = current_date.strftime('%Y%m%d')
        folder_save = os.path.join(files_folder, 'Dados', d)

        if not os.path.exists(folder_save):
            os.makedirs(folder_save)

        base_url = "https://embracedata.inpe.br/magnetometer/"
        variable_url = f"{station}/{current_date.year}/"
        final_url = urljoin(base_url, variable_url)

        response = requests.get(final_url, verify=False)
        if response.status_code != 200:
            print(f"Failed to access data for {current_date.strftime('%Y-%m-%d')}")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')

        for link in soup.find_all('a'):
            file_name = link.get('href')
            if file_name == "../" or not file_name.endswith(f'.{current_date.year % 100}m'):
                continue

            wanted_date = current_date.strftime("%d%b").lower()
            file_date = file_name[3:8]

            if wanted_date == file_date:
                local_file_path = os.path.join(folder_save, file_name)
                if os.path.exists(local_file_path):
                    print(f"[{file_name}] Already on the disk")
                else:
                    file_url = urljoin(final_url, file_name)
                    print(f"[{file_name}] Downloaded")
                    with open(local_file_path, 'wb') as file:
                        file_response = requests.get(file_url, verify=False)
                        file.write(file_response.content)

                if combined_file_name is None:
                    combined_file_name = file_name
                    combined_file_path = os.path.join(files_folder, combined_file_name)

                # Append the content to the combined file
                with open(combined_file_path, 'ab') as combined_file:
                    with open(local_file_path, 'rb') as file:
                        combined_file.write(file.read())

    if combined_file_name:
        print(f"Combined file saved at: {combined_file_path}")
        df, _ = process_data(combined_file_path, date_str)
        return df
    else:
        print("No files were downloaded.")
        return None

def intermagnet_download(files_folder, date_str, station, duration):
    date = datetime.strptime(date_str, "%Y-%m-%d")
    half_duration = (duration - 1) // 2
    start_date = date - timedelta(days=half_duration)
    end_date = date + timedelta(days=half_duration)

    combined_file_name = f'{station.lower()}{date_str.replace("-", "")}vmin.min'
    combined_file_path = os.path.join(files_folder, combined_file_name)

    for day_offset in range((end_date - start_date).days + 1):
        current_date = start_date + timedelta(days=day_offset)
        d = current_date.strftime('%Y%m%d')
        url = "https://imag-data.bgs.ac.uk/GIN_V1/GINServices"
        params = {
            "Request": "GetData",
            "format": "Iaga2002",
            "testObsys": 0,
            "observatoryIagaCode": station,
            "samplesPerDay": "minute",
            "publicationState": "Best available",
            "dataStartDate": current_date.strftime('%Y-%m-%d'),
            "dataDuration": 1
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.text
            save_folder = os.path.join(files_folder, 'Dados', d)
            file_name = f'{station.lower()}{d}vmin.min'
            full_save_path = os.path.join(save_folder, file_name)

            if not os.path.exists(save_folder):
                os.makedirs(save_folder)

            if os.path.exists(full_save_path):
                print(f"[{file_name}] Already on the disk")
            else:
                with open(full_save_path, "w") as file:
                    file.write(data)
                print(f"[{file_name}] Downloaded")

            # Append the content to the combined file
            with open(combined_file_path, 'a') as combined_file:
                combined_file.write(data)
        else:
            print(f"Failed to download data for {current_date.strftime('%Y-%m-%d')}")

    df, _ = process_data(combined_file_path, date_str)
    return df

# Exemplo de uso:
df_embrace = download_embrace("./Dados", "2024-05-10", "SMS", 3)
df_intermagnet = intermagnet_download("./Dados", "2024-05-10", "SMS", 3)

# Exemplo de uso:
df_SMS = download_embrace("", "2024-05-10", "SMS", 3)
df_ASC = intermagnet_download("", "2024-05-10", "ASC", 3)
df_KDU = intermagnet_download("", "2024-05-10", "KDU", 3)