import json
import csv
import re
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from lxml import etree as ET
import ollama
import datetime
import os
import threading
import time

LOG_FILE = "seo_log.txt"

def log_to_file(message):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now()}] {message}\n")

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def generate_seo_data(title):
    system_prompt = (
        "Jesteś ekspertem SEO i copywriterem. "
        "Zawsze generuj odpowiedzi wyłącznie po polsku, niezależnie od treści tytułu. "
        "Twoim zadaniem jest stworzyć: SEO tytuł, opis treści, meta tytuł, meta opis, krótki opis oraz tagi SEO. "
        "Używaj języka naturalnego, przyjaznego dzieciom i rodzicom. "
        "Strona kolorowanki.site oferuje darmowe kolorowanki do druku."
    )

    prompt = f"""Tytuł wpisu: "{title}"

Zwróć odpowiedź w formacie JSON:
{{
  "seo_title": "...",
  "seo_content": "...",
  "meta_title": "...",
  "meta_description": "...",
  "excerpt": "...",
  "seo_tags": ["...", "...", "..."]
}}"""

    try:
        response = ollama.chat(model="mistral", messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ])
        return json.loads(response['message']['content'].strip())
    except Exception as e:
        log_to_file(f"Błąd podczas generowania SEO: {e}")
        return None

def extract_cdata(element):
    return element.text if element is not None and element.text else ""

def set_cdata(element, tag, new_cdata):
    target_element = element.find(tag)
    if target_element is None:
        target_element = ET.SubElement(element, tag)
    target_element.text = ET.CDATA(new_cdata)

def add_postmeta(item, key, value):
    postmeta = ET.SubElement(item, "{http://wordpress.org/export/1.2/}postmeta")
    ET.SubElement(postmeta, "{http://wordpress.org/export/1.2/}meta_key").text = key
    ET.SubElement(postmeta, "{http://wordpress.org/export/1.2/}meta_value").text = value

class SEOApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Generator SEO z XML WordPress")

        self.select_button = tk.Button(root, text="Wybierz plik XML", command=self.select_file)
        self.select_button.pack(pady=10)

        self.log_area = scrolledtext.ScrolledText(root, width=100, height=30, state='disabled')
        self.log_area.pack()

        self.stop_button = tk.Button(root, text="Zatrzymaj", command=self.stop_process, state='disabled')
        self.stop_button.pack(pady=5)

        self.pause_button = tk.Button(root, text="Pauza", command=self.pause_process, state='disabled')
        self.pause_button.pack(pady=5)

        self.resume_button = tk.Button(root, text="Wznów", command=self.resume_process, state='disabled')
        self.resume_button.pack(pady=5)

        self.processing = False
        self.paused = False
        self.stop_flag = False

    def log(self, message):
        self.log_area.configure(state='normal')
        self.log_area.insert(tk.END, message + '\n')
        self.log_area.configure(state='disabled')
        self.log_area.see(tk.END)
        log_to_file(message)

    def select_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Pliki XML", "*.xml")])
        if filepath:
            self.process_file(filepath)

    def process_file(self, filepath):
        self.processing = True
        self.stop_flag = False
        self.pause_button.configure(state='normal')
        self.stop_button.configure(state='normal')

        thread = threading.Thread(target=self.process_xml_file, args=(filepath,))
        thread.start()

    def process_xml_file(self, filepath):
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            csv_rows = []

            nsmap = {
                'content': 'http://purl.org/rss/1.0/modules/content/',
                'excerpt': 'http://wordpress.org/export/1.2/',
                'wp': 'http://wordpress.org/export/1.2/'
            }

            for item in root.findall(".//item"):
                if self.stop_flag:
                    self.log("🛑 Przerwano przetwarzanie.")
                    break

                if self.paused:
                    while self.paused and not self.stop_flag:
                        time.sleep(1)

                title_el = item.find("title")
                title = clean_text(title_el.text if title_el is not None else "Brak tytułu")
                self.log(f"🔄 Generuję SEO dla: {title}")
                seo_data = generate_seo_data(title)

                if seo_data is None:
                    self.log(f"❌ Błąd generowania SEO dla: {title}. Pomijam.")
                    continue

                set_cdata(item, "{http://wordpress.org/export/1.2/}encoded", seo_data['excerpt'])

                content_el = item.find("content:encoded", namespaces=nsmap)
                original_content = extract_cdata(content_el)
                content_parts = original_content.split("</script>")
                html_content = content_parts[0] + "</script>" if len(content_parts) > 1 else original_content
                new_content = f"{html_content}\n\n<h2>{seo_data['seo_title']}</h2>\n{seo_data['seo_content']}"
                set_cdata(item, "{http://purl.org/rss/1.0/modules/content/}encoded", new_content)

                add_postmeta(item, "meta_title", seo_data['meta_title'])
                add_postmeta(item, "meta_description", seo_data['meta_description'])
                add_postmeta(item, "seo_tags", ', '.join(seo_data['seo_tags']))

                csv_rows.append({
                    "title": title,
                    "seo_title": seo_data["seo_title"],
                    "meta_title": seo_data["meta_title"],
                    "meta_description": seo_data["meta_description"],
                    "excerpt": seo_data["excerpt"],
                    "seo_tags": ", ".join(seo_data["seo_tags"]),
                })

            if not self.stop_flag:
                output_base = os.path.splitext(os.path.basename(filepath))[0]
                output_xml = output_base + "-z-seo.xml"
                output_csv = output_base + "-z-seo.csv"

                tree.write(output_xml, encoding="utf-8", xml_declaration=True, pretty_print=True)

                with open(output_csv, mode='w', encoding='utf-8', newline='') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=csv_rows[0].keys())
                    writer.writeheader()
                    writer.writerows(csv_rows)

                self.log(f"✅ Gotowe!\nPlik XML: {output_xml}\nPlik CSV: {output_csv}")

        except Exception as e:
            self.log(f"❗ Błąd: {str(e)}")

        self.processing = False
        self.stop_button.configure(state='disabled')
        self.pause_button.configure(state='disabled')
        self.resume_button.configure(state='disabled')

    def stop_process(self):
        self.stop_flag = True
        self.log("🛑 Przerywam przetwarzanie...")

    def pause_process(self):
        self.paused = True
        self.pause_button.configure(state='disabled')
        self.resume_button.configure(state='normal')
        self.log("⏸️ Pauza...")

    def resume_process(self):
        self.paused = False
        self.resume_button.configure(state='disabled')
        self.pause_button.configure(state='normal')
        self.log("▶️ Wznowiono przetwarzanie.")

if __name__ == "__main__":
    root = tk.Tk()
    app = SEOApp(root)
    root.mainloop()
