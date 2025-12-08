import requests
import re
import os
import json

def update_playlist():
    original_url = "https://iptv-ch.github.io/netplus.mpd"
    # URL di un database EPG pubblico per mappare tvg-id a codici paese
    # Useremo il database di iptv-org come riferimento
    channel_map_url = "https://iptv-org.github.io/api/channels.json"
    output_filename = "netplus_modified.mpd"

    # 1. Scarica la mappa dei canali esterna
    try:
        response = requests.get(channel_map_url)
        response.raise_for_status()
        channels_data = response.json()
        
        # Crea un dizionario di mappatura: { "tvg-id": "CountryName" }
        tvg_id_to_country = {}
        for channel in channels_data:
            if 'id' in channel and 'country' in channel:
                 tvg_id_to_country[channel['id']] = channel['country']

    except requests.exceptions.RequestException as e:
        print(f"Errore durante il download della mappa canali: {e}")
        # Se fallisce, usiamo una mappa vuota e i canali finiranno in 'Others'
        tvg_id_to_country = {}


    # 2. Scarica e modifica la playlist originale
    try:
        response = requests.get(original_url)
        response.raise_for_status()
        content = response.text

        lines = content.split('\n')
        modified_lines = []

        for line in lines:
            if line.startswith('#EXTINF'):
                tvg_id_match = re.search(r'tvg-id="([^"]+)"', line)
                group_tag = "Others" # Default 'Others'

                if tvg_id_match:
                    tvg_id_value = tvg_id_match.group(1)
                    # Cerca l'ID nel dizionario che abbiamo creato
                    if tvg_id_value in tvg_id_to_country:
                        country_code = tvg_id_to_country[tvg_id_value]
                        # Mappa i codici a nomi di gruppo puliti
                        if country_code == 'IT':
                            group_tag = "Italian"
                        elif country_code == 'FR':
                            group_tag = "French"
                        elif country_code == 'DE':
                            group_tag = "German"
                        elif country_code == 'ES':
                            group_tag = "Spanish"
                        elif country_code == 'CH':
                            group_tag = "Swiss"
                        elif country_code == 'UK':
                            group_tag = "English"
                        elif country_code == 'US':
                            group_tag = "English"
                            
                        else:
                            group_tag = country_code # Usa il codice se non è mappato sopra


                # Aggiungi o aggiorna l'attributo group-title
                if re.search(r'group-title="[^"]+"', line):
                    line = re.sub(r'group-title="[^"]+"', f'group-title="{group_tag}"', line)
                else:
                    last_comma_index = line.rfind(',')
                    if last_comma_index != -1:
                        line = line[:last_comma_index] + f' group-title="{group_tag}"' + line[last_comma_index:]
                    else:
                        line = line.strip() + f' group-title="{group_tag}"'

                modified_lines.append(line)
            else:
                modified_lines.append(line)

        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(modified_lines))

        print(f"Playlist modificata salvata in {output_filename} usando la mappa EPG esterna.")

    except requests.exceptions.RequestException as e:
        print(f"Errore durante il download della playlist: {e}")
        exit(1)

if __name__ == "__main__":
    update_playlist()
