# SEO Generator dla Kolorowanek

## Opis
SEO Generator dla Kolorowanek to aplikacja stworzona w Pythonie, której celem jest automatyczne generowanie danych SEO dla postów z kolorowankami na platformie WordPress. Aplikacja pozwala na:
- Dodawanie meta tytułów, opisów oraz tagów SEO do postów w pliku XML eksportowanym z WordPressa,
- Generowanie SEO tytułów, meta tytułów, meta opisów i tagów na podstawie tytułów kolorowanek,
- Modyfikację treści HTML kolorowanek, by były przyjazne SEO i bardziej angażujące.

## Funkcje
- **SEO Title**: Generowanie tytułu SEO na podstawie tytułu kolorowanki.
- **SEO Content**: Tworzenie treści SEO przyjaznej dzieciom i rodzicom, na podstawie tytułu kolorowanki.
- **Meta Title i Meta Description**: Dodawanie meta tytułów i opisów do XML-a.
- **SEO Tags**: Generowanie odpowiednich tagów SEO na podstawie tytułów.
- **Pauza i wznowienie**: Możliwość zatrzymania, pauzowania i wznowienia procesu przetwarzania.

## Jak zainstalować
1. Sklonuj to repozytorium:
    ```bash
    git clone https://github.com/username/seo-generator-kolorowanki.git
    ```
2. Przejdź do folderu projektu:
    ```bash
    cd seo-generator-kolorowanki
    ```
3. Zainstaluj wymagane biblioteki:
    ```bash
    pip install -r requirements.txt
    ```
4. Uruchom aplikację:
    ```bash
    python seo_generator_gui.py
    ```

## Jak używać
1. Uruchom aplikację.
2. Kliknij przycisk "Wybierz plik XML", aby załadować plik XML eksportowany z WordPressa.
3. Aplikacja rozpocznie generowanie danych SEO dla postów kolorowanek w pliku XML.
4. Możesz wstrzymać przetwarzanie (przycisk Pauza), wznowić je (przycisk Wznów) lub zatrzymać (przycisk Zatrzymaj).
5. Zmodyfikowane pliki XML i CSV zostaną zapisane w tym samym katalogu co plik wejściowy, z odpowiednimi suffixami `-z-seo`.

## Struktura pliku XML
Aplikacja przetwarza plik XML, który jest eksportem z WordPressa, zawierający elementy `<item>`. W każdym elemencie `<item>` generowane są dane SEO dla:
- SEO tytułu (`meta_title`),
- Opisów (`meta_description`, `seo_content`),
- Tytułu SEO (`seo_title`),
- Tagów SEO.

## Jak działa aplikacja?
1. **Wybór pliku XML** – Użytkownik wybiera plik XML eksportowany z WordPressa.
2. **Generowanie danych SEO** – Aplikacja automatycznie generuje dane SEO (SEO title, meta title, meta description, etc.) dla każdej kolorowanki na podstawie tytułów.
3. **Modyfikacja XML** – Aplikacja modyfikuje zawartość XML, wstawiając odpowiednie metadane oraz generując nowe treści SEO.
4. **Zapis plików** – Zmodyfikowany plik XML jest zapisywany z sufiksem `-z-seo.xml`, a dane SEO są eksportowane do pliku CSV w formacie tabelarycznym.

## Wymagania
- Python 3.7+
- Biblioteki: `xml.etree.ElementTree`, `lxml`, `tkinter`, `ollama`, `re`, `csv`

## Licencja
Ten projekt jest objęty licencją MIT. Zobacz plik LICENSE, aby uzyskać więcej informacji.
