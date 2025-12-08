import requests
import re
import os

def update_playlist():
    original_url = "https://iptv-ch.github.io/netplus.mpd"
    output_filename = "netplus_modified.mpd"

    try:
        response = requests.get(original_url)
        response.raise_for_status()
        content = response.text

        lines = content.split('\n')
        modified_lines = []

        for line in lines:
            if line.startswith('#EXTINF'):
                tvg_id_match = re.search(r'tvg-id="([^"]+)"', line)
                group_tag = "Others" # Default a 'Others' se non troviamo corrispondenze

                if tvg_id_match:
                    tvg_id_value = tvg_id_match.group(1).lower()
                    
                    if '.it' in tvg_id_value:
                        group_tag = "Italian"
                    elif '.fr' in tvg_id_value:
                        group_tag = "French"
                    elif '.de' in tvg_id_value:
                        group_tag = "German"
                    elif '.ch' in tvg_id_value:
                        group_tag = "Swiss"
                    # Inizio nuove estensioni aggiunte:
                    elif '.uk' in tvg_id_value:
                        group_tag = "UK"
                    elif '.at' in tvg_id_value:
                        group_tag = "Austrian"
                    elif '.be' in tvg_id_value:
                        group_tag = "Belgian"
                    elif '.es' in tvg_id_value:
                        group_tag = "Spanish"
                    elif '.pt' in tvg_id_value:
                        group_tag = "Portuguese"
                    elif '.br' in tvg_id_value:
                        group_tag = "Brazilian"
                    elif '.nl' in tvg_id_value:
                        group_tag = "Dutch"
                    elif '.pl' in tvg_id_value:
                        group_tag = "Polish"
                    elif '.hu' in tvg_id_value:
                        group_tag = "Hungarian"
                    elif '.rs' in tvg_id_value:
                        group_tag = "Serbian"
                    elif '.ng' in tvg_id_value:
                        group_tag = "Nigerian"
                    elif '.jp' in tvg_id_value:
                        group_tag = "Japanese"
                    elif '.tr' in tvg_id_value:
                        group_tag = "Turkish"
                    elif '.ma' in tvg_id_value:
                        group_tag = "Moroccan"
                    elif '.eg' in tvg_id_value:
                        group_tag = "Egyptian"
                    elif '.cn' in tvg_id_value:
                        group_tag = "Chinese"
                    elif '.xk' in tvg_id_value:
                        group_tag = "Kosovan"
                    elif '.me' in tvg_id_value:
                        group_tag = "Montenegrin"
                    # Estensioni generiche/internazionali
                    elif '.com' in tvg_id_value or '.net' in tvg_id_value or '.tv' in tvg_id_value:
                        group_tag = "International"
                    # Fine nuove estensioni

                # Aggiungi o aggiorna l'attributo group-title
                if re.search(r'group-title="[^"]+"', line):
                    # Se esiste già, sostituisci il valore
                    line = re.sub(r'group-title="[^"]+"', f'group-title="{group_tag}"', line)
                else:
                    # Se non esiste, aggiungilo alla fine della riga EXTINF, prima del nome del canale
                    last_comma_index = line.rfind(',')
                    if last_comma_index != -1:
                        line = line[:last_comma_index] + f' group-title="{group_tag}"' + line[last_comma_index:]
                    # Se non c'è virgola (caso strano), lo aggiungiamo in coda
                    else:
                        line = line.strip() + f' group-title="{group_tag}"'


                modified_lines.append(line)
            else:
                modified_lines.append(line)

        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(modified_lines))

        print(f"Playlist modificata salvata in {output_filename} usando i tag tvg-id.")

    except requests.exceptions.RequestException as e:
        print(f"Errore durante il download della playlist: {e}")
        exit(1)

if __name__ == "__main__":
    update_playlist()
