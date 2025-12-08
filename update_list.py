import requests
import re
import os
import json

def get_country_name(code):
    """Mappa i codici nazione ISO a nomi di gruppo puliti."""
    if code == 'IT': return "Italian"
    if code == 'FR': return "French"
    if code == 'DE': return "German"
    if code == 'ES': return "Spanish"
    if code == 'CH': return "Swiss"
    return code # Ritorna il codice se non è mappato sopra

def update_playlist():
    original_url = "https://iptv-ch.github.io/netplus.mpd"
    channel_map_url_external = "https://iptv-org.github.io/api/channels.json"
    output_filename = "netplus_modified.mpd"
    
    external_map_data = {}
    
    # --- 1. Scarica la mappa esterna IPTV-Org (Priorità 1) ---
    try:
        response = requests.get(channel_map_url_external)
        response.raise_for_status()
        channels_data = response.json()
        for channel in channels_data:
            if 'id' in channel and 'country' in channel:
                 external_map_data[channel['id']] = channel['country']
        print(f"Mappa canali esterni caricata con {len(external_map_data)} entries.")
    except requests.exceptions.RequestException:
        print("Errore durante il download della mappa canali esterna. Proseguo senza di essa.")

    # --- 2. Elabora la playlist ---
    try:
        response = requests.get(original_url)
        response.raise_for_status()
        content = response.text

        lines = content.split('\n')
        modified_lines = []

        for line in lines:
            if line.startswith('#EXTINF'):
                group_tag = "Others" # Default finale
                tvg_id_match = re.search(r'tvg-id="([^"]+)"', line)
                channel_name = line.split(',')[-1].strip().lower()
                
                tvg_id_value = tvg_id_match.group(1) if tvg_id_match else None

                # A. Priorità 1: Usa il database esterno (se l'ID è presente)
                if tvg_id_value and tvg_id_value in external_map_data:
                    country_code = external_map_data[tvg_id_value]
                    group_tag = get_country_name(country_code)
                
                # B. Priorità 2: Analisi del tvg-id per estensione (se A fallisce)
                if group_tag == "Others" and tvg_id_value:
                    if tvg_id_value.endswith('.it'): group_tag = "Italian"
                    elif tvg_id_value.endswith('.fr'): group_tag = "French"
                    elif tvg_id_value.endswith('.de'): group_tag = "German"
                    elif tvg_id_value.endswith('.ch'): group_tag = "Swiss"

                # C. Priorità 3: Analisi del nome del canale (se B fallisce)
                if group_tag == "Others" and channel_name:
                    if 'rai' in channel_name or 'italia' in channel_name or 'italy' in channel_name or 'mediaset' in channel_name: group_tag = "Italian"
                    elif 'france' in channel_name or 'f2' in channel_name or 'm6' in channel_name: group_tag = "French"
                    elif 'german' in channel_name or 'zdf' in channel_name or 'ard' in channel_name: group_tag = "German"
                    elif 'rts' in channel_name or 'srf' in channel_name or 'rsi' in channel_name or 'svizzera' in channel_name: group_tag = "Swiss"

                # D. Applica il group-title alla riga
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
