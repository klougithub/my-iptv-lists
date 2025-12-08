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
                # Usa una RegEx per trovare il valore di tvg-id="VALUE"
                tvg_id_match = re.search(r'tvg-id="([^"]+)"', line)
                group_tag = "UNKNOWN"

                if tvg_id_match:
                    tvg_id_value = tvg_id_match.group(1).lower()
                    
                    if '.it' in tvg_id_value:
                        group_tag = "ITALY"
                    elif '.fr' in tvg_id_value:
                        group_tag = "FRANCE"
                    elif '.de' in tvg_id_value:
                        group_tag = "GERMANY"
                    elif '.ch' in tvg_id_value:
                        group_tag = "SWITZERLAND"
                    # Puoi aggiungere altri paesi qui se necessario (.co.uk, .us, etc.)

                # Aggiungi o aggiorna l'attributo group-title
                # Usiamo re.sub per sostituire group-title se esiste già, altrimenti lo aggiungiamo
                if re.search(r'group-title="[^"]+"', line):
                    line = re.sub(r'group-title="[^"]+"', f'group-title="{group_tag}"', line)
                else:
                    # Aggiungi il group-title subito dopo tvg-id per mantenere l'ordine
                    line = line.replace(tvg_id_match.group(0), f'{tvg_id_match.group(0)} group-title="{group_tag}"')

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
