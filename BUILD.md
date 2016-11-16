
JFR Pary - dane licytacji: Informacje dla programistów
======================================================

Struktura repozytorium kodu
---------------------------

Katalog [`src`](src) zawiera komponenty źródłowe programu:

* [kod skryptu Pythona](src/bidding_data.py), który wykonuje całą robotę
* [kod skryptu pakującego program w interfejs graficzny](src/bidding_data_gui.py)
* [ikonę programu](src/icon.ico) wraz ze [źródłami](src/icon.xcf)
* [metadane programu](src/version) dla PyInstallera

Katalog [`res`](res) zawiera pliki dołączane do programu: style, skrypty JS i grafikę.

Katalogi `dist` i `build` są domyślnie puste i są katalogami roboczymi
PyInstallera.

Katalog [`bundle`](bundle) zawiera wynikowe paczki ZIP z kolejnymi wersjami programu.

W katalogu głównym znajdują się rozmaite README oraz skrypty budujące program.

Od zera do bohatera - proces budowania programu
-----------------------------------------------

Jedynym wymaganym do działania narzędzia elementem repozytorium jest źródłowy
skrypt [`bidding_data.py`](src/bidding_data.py). Cała reszta to tylko
fajerwerki i opakowanie w plik wykonywalny.

Skrypt można uruchomić w dowolnym środowisku, w którym działa Python, a jego
wymagania wymienione są poniżej. `bidding_data.py` przyjmuje parametry
identycznie do wynikowego pliku wykonywalnego.

Wersja z głównej gałęzi repozytorium działa jedynie pod Windowsem, z racji
używania podłączania się bezpośrednio do pliku BWS poprzez Accessowe ODBC.
Gałąź `csv` zawiera kompatybilną między systemami operacyjnymi wersję operującą
na danych podanych w plikach CSV, do których można wyeksportować dane z BWS.

Skrypt z gałęzi `csv` jest w pełni funkcjonalny, acz obdarty z fajerwerków.
Może również nie być dalej rozwijany, w zależności od upierdliwości scalania
zmian.

---

Pliku źródłowego można użyć jako modułu, jeśli kogoś to kręci, importując go
do swojej aplikacji poprzez:
```
from bidding_data import JFRBidding
```

---

Skrypt można samodzielnie skompilować do pliku wykonywalnego, używając do tego
PyInstallera. Można to zrobić z pomocą dołączonego pliku [`bidding_data.spec`](bidding_data.spec):
```
pyinstaller bidding_data.spec
```
lub samodzielnie, podając odpowiednie parametry do PyInstallera:
```
pyinstaller --onefile --version-file=src\version --icon=src\icon.ico src\bidding_data.py
```
Zarówno metadane z pliku `src/version`, jak i ikona programu są w 100% opcjonalne.

Wynik działania PyInstallera (pojedynczy plik wykonywalny) znajdzie się w katalogu `dist`.

---

Skrypt wsadowy [`MAKE.bat`](MAKE.bat) pakuje potrzebne do dystrybucji programu dane
w jedną, zgrabną paczkę. Uruchamia on jedynie skrypt Windows PowerShell [`MAKE.ps1`](MAKE.ps1),
który, kolejno:

* kompiluje EXE przy użyciu PyInstallera
* kopiuje README do katalogu `dist`
* kopiuje zasoby z `res` do katalogu `dist`
* odczytuje metadane utworzonego EXE
* tworzy z nich nazwę dla paczki
* pakuje cały katalog `dist` do paczki i umieszcza ją w `bundle`

---

Analogiczny proces dla interfejsu graficznego polega na podmianie skryptu
źródłowego z src/bidding_data.py na src/bidding_data_gui.py (dołącza sobie
bidding_data.py jako moduł) i wywołanie pyinstallera z opcją aplikacji
okienkowej.

Wymagania systemowe
-------------------

Skrypt [`bidding_data.py`](src/bidding_data.py):

* python 2.x (testowane i tworzone w wersji 2.7.10)
* BeautifulSoup4
* lxml (jako parser dla BS4)
* argparse
* pypyodbc

Kompilacja do EXE:

* [PyInstaller](http://pythonhosted.org/PyInstaller/)
* PyWin32

Zbudowanie paczki z [`bundle`](bundle):

* Windows PowerShell (4.0)
* .NET 4.5

Interfejs graficzny (dodatkowo):

* Tkinter

Znane problemy
--------------

* .NET 4.5 to .NET 4.5, nie .NET 4.5 Client Profile. W niepełnej wersji może
nie być DLLki z System.IO.Compression.FileSystem importowanej przez skrypt
PowerShella.
* PyInstaller nie lubi kompilować ze ścieżek ze znakami nie-ASCII. `¯\_(ツ)_/¯`
* co więcej, jego wersja stabilna produkuje .exe, które nie odpala się
z niektórych ścieżek nie-ASCII:
https://github.com/pyinstaller/pyinstaller/issues/1396
(.exe dostarczane w `dist` powinno działać)
* od czasu pierwszej wersji aplikacji, PyInstaller ruszył bardzo mocno
do przodu, gdybym miał określić, w której wersji projekt buduje się
bez problemu, musiałbym ponownie użyć: `¯\_(ツ)_/¯` - czasem działa 2.2.1
z ręcznym patchem na problemy wymienione powyżej, czasem 3.3, ostatnio działała
3.3.dev0+b78bfe5
* "ostatnio" również w/w wersja "działała", ale kompilowane EXE nie uruchamiało
się pod niektórymi systemami (cześć, Olo), z racji błędu wprowadzonego gdzieś
około wersji 3.2; po cofnięciu do 3.1, PyInstaller nie radził sobie, gdy katalog
roboczy `build` nie był pusty (próby nadpisywania własnych plików `.egg`) oraz
losowo nie udaje mu się aktualizować metadanych kompilowanego EXE (częściej niż
rzadziej)
* Avast (i być może inne antywirusy) lubią zapobiegać próbom modyfikacji
metadanych plików EXE - błąd "Odmowa dostępu [Errno 5]"

Kod żródłowy
------------

Kod źródłowy stara się, z grubsza:

* zgadzać ze standardami [PEP8](https://www.python.org/dev/peps/pep-0008/)
* nie robić [głupich rzeczy](http://stackoverflow.com/a/1732454)
* nie psuć raz przekształconej strony przy próbie ponownego przekształcenia
* komentować rzeczy nieoczywiste

Operacje na stronach JFR
------------------------

Ramowy algorytm działania programu:

1. Wczytać dane z BWS: tabela `BiddingData` zawiera dane licytacji, tabela
`RoundData` zawiera dane rund (numery rozdań, numery par itp.).
2. Zmapować numery rozdań JFR Pary (jedna, ciągła numeracja dla całego turnieju)
na numery rozdań fizycznych pudełek na sali (numery rozdań w BWS).
3. Skompilować tabele z licytacjami i zapisać je do osobnych plików. Format
nazwy pliku to `[PREFIX_JFR]_bidding_[NUMER_JFR]_[NUMERY_PAR].txt`. Numery par
w nazwie pliku posortowane są rosnąco. Każdy plik zawiera gotowy kod HTML
z licytacją.
4. Dołączyć do plików protokołów (`[PREFIX_JFR][NUMER_JFR].html`) skrypty JS
niezbędne do pokazania licytacji w protokole (jQuery i [`bidding.js`](res/javas/bidding.js)).
5. W plikach zawartości protokołów (`[PREFIX_JFR][NUMER_JFR].txt`), do każdego wiersza,
dla którego dysponujemy licytacją, dołączyć link pokazujący licytację.

Program obsługuje wiele rozdań o tym samym numerze w jednym BWS i mapuje
rozdania na odpowiednie numery JFR na podstawie zestawu danych: nr stołu
(z sektorem), nr rundy, nr pudełka rozdaniowego.

---

`Hello image, sing me a line from your favourite song.`
