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

    tvg_id_to_country = {}
    
    # --- TENTATIVO 1: Scarica la mappa esterna ---
    try:
        response = requests.get(channel_map_url)
        response.raise_for_status()
        channels_data = response.json()
        for channel in channels_data:
            if 'id' in channel and 'country' in channel:
                 tvg_id_to_country[channel['id']] = channel['country']
        print(f"Mappa canali esterni caricata con {len(tvg_id_to_country)} entries.")

    except requests.exceptions.RequestException as e:
        print(f"Errore durante il download della mappa canali esterna. Proseguo senza di essa.")


    # --- TENTATIVO 2: Elabora la playlist ---
    try:
        response = requests.get(original_url)
        response.raise_for_status()
        content = response.text

        lines = content.split('\n')
        modified_lines = []

        for line in lines:
            if line.startswith('#EXTINF'):
                group_tag = "Others" # Default

                tvg_id_match = re.search(r'tvg-id="([^"]+)"', line)
                channel_name = line.split(',')[-1].strip().lower()

                # A. Prova a usare il database esterno (Priorità)
                if tvg_id_match and tvg_id_match.group(1) in tvg_id_to_country:
                    country_code = tvg_id_to_country[tvg_id_match.group(1)]
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
                    else:
                        group_tag = country_code

                # B. Se il database esterno non ha funzionato, usa il nome del canale (Fallback)
                else:
                    if 'rai' in channel_name or 'italia' in channel_name or 'italy' in channel_name or 'mediaset' in channel_name:
                        group_tag = "Italian"
                    elif 'france' in channel_name or 'f2' in channel_name or 'm6' in channel_name or 'arte' in channel_name:
                        group_tag = "French"
                    elif 'german' in channel_name or 'zdf' in channel_name or 'ard' in channel_name or 'rtl' in channel_name:
                        group_tag = "German"
                    elif 'tve' in channel_name or 'espan' in channel_name or 'spain' in channel_name:
                        group_tag = "Spanish"
                    elif 'rts' in channel_name or '.ch' in channel_name or 'svizzera' in channel_name or 'srf' in channel_name or 'rsi' in channel_name:
                        group_tag = "Swiss"
                
                # C. Applica il group-title alla riga
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

        print(f"Playlist modificata salvata in {output_filename}.")

    except requests.exceptions.RequestException as e:
        print(f"Errore durante il download della playlist: {e}")
        exit(1)

if __name__ == "__main__":
    update_playlist()
