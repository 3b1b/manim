<p align="center">
    <a href="https://github.com/3b1b/manim">
        <img src="https://raw.githubusercontent.com/3b1b/manim/master/logo/cropped.png">
    </a>
</p>

[![pypi version](https://img.shields.io/pypi/v/manimgl?logo=pypi)](https://pypi.org/project/manimgl/)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat)](http://choosealicense.com/licenses/mit/)
[![Manim Subreddit](https://img.shields.io/reddit/subreddit-subscribers/manim.svg?color=ff4301&label=reddit&logo=reddit)](https://www.reddit.com/r/manim/)
[![Manim Discord](https://img.shields.io/discord/581738731934056449.svg?label=discord&logo=discord)](https://discord.com/invite/bYCyhM9Kz2)
[![docs](https://github.com/3b1b/manim/workflows/docs/badge.svg)](https://3b1b.github.io/manim/)

Manim è un motore per animazioni programmatiche precise, progettato per la creazione di video matematici esplicativi.

Nota: esistono due versioni di Manim. Questo repository è nato come progetto personale dell'autore di [3Blue1Brown](https://www.3blue1brown.com/) allo scopo di animare quei video, con il codice specifico per i video disponibile [qui](https://github.com/3b1b/videos). Nel 2020 un gruppo di sviluppatori lo ha forkato in quella che oggi è la [community edition](https://github.com/ManimCommunity/manim/), con l'obiettivo di essere più stabile, meglio testata, più rapida nel rispondere ai contributi della community e, in generale, più facile da approcciare. Consulta [questa pagina](https://docs.manim.community/en/stable/faq/installation.html#different-versions) per maggiori dettagli.

## Installazione
> [!Warning]
> **ATTENZIONE:** Queste istruzioni sono valide *solo* per ManimGL. Cercare di utilizzare queste istruzioni per installare [Manim Community/manim](https://github.com/ManimCommunity/manim), o seguire le istruzioni di quel repository per installare questa versione, causerà problemi. Dovresti prima decidere quale versione desideri installare e seguire esclusivamente le istruzioni per la versione scelta.

> [!Note]
> **Nota**: Per installare manim direttamente tramite pip, fai attenzione al nome del pacchetto installato. Questo repository è ManimGL di 3b1b. Il nome del pacchetto è `manimgl` invece di `manim` o `manimlib`. Per favore usa `pip install manimgl` per installare la versione in questo repository.

Manim funziona su Python 3.7 o superiore.

I requisiti di sistema sono [FFmpeg](https://ffmpeg.org/), [OpenGL](https://www.opengl.org/) e [LaTeX](https://www.latex-project.org) (opzionale, se desideri usare LaTeX).
Per Linux, sono richiesti [Pango](https://pango.org) insieme ai suoi header di sviluppo. Vedi le istruzioni [qui](https://github.com/ManimCommunity/ManimPango#building).


### Direttamente

```sh
# Install manimgl
pip install manimgl

# Try it out
manimgl
```

Per ulteriori opzioni, dai un'occhiata alle sezioni [Utilizzare Manim](#using-manim) più avanti.

Se vuoi lavorare sul codice sorgente di manimlib stesso, clona questo repository e nella directory esegui:

```sh
# Install manimgl
pip install -e .

# Try it out
manimgl example_scenes.py OpeningManimExample
# or
manim-render example_scenes.py OpeningManimExample
```

### Direttamente (Windows)

1. [Installa FFmpeg](https://www.wikihow.com/Install-FFmpeg-on-Windows).
2. Installa una distribuzione LaTeX. [MiKTeX](https://miktex.org/download) è raccomandata.
3. Installa i restanti pacchetti Python.
    ```sh
    git clone https://github.com/3b1b/manim.git
    cd manim
    pip install -e .
    manimgl example_scenes.py OpeningManimExample
    ```

### Mac OSX

1. Installa FFmpeg, LaTeX nel terminale usando homebrew.
    ```sh
    brew install ffmpeg mactex
    ```
    <details>
      <summary>💡 Un'alternativa al bundle pesante MacTeX.</summary>

      > Per evitare di installare l'intero bundle MacTeX, che pesa circa 6GB, puoi installare in alternativa il
      > leggero [BasicTeX](https://formulae.brew.sh/cask/basictex) e poi aggiungere gradualmente
      > solo i pacchetti LaTeX di cui hai effettivamente bisogno. Un elenco di pacchetti sufficienti per eseguire gli esempi può 
      > essere trovato [qui](https://github.com/3b1b/manim/issues/2133#issuecomment-2414547866).
      > Per una panoramica dei bundle di installazione di MacTeX, vedi https://www.tug.org/mactex/.
    </details>

2. Se stai usando un processore basato su ARM, installa Cairo. 
    ```sh
    arch -arm64 brew install pkg-config cairo
    ```
   
3. Installa l'ultima versione di manim usando questi comandi.
    ```sh
    git clone https://github.com/3b1b/manim.git
    cd manim
    pip install -e .
    manimgl example_scenes.py OpeningManimExample (assicurati di aggiungere prima manimgl al path.)
    ```

## Installazione Anaconda

1. Installa LaTeX come indicato sopra.
2. Crea un ambiente conda usando `conda create -n manim python=3.9`.
3. Attiva l'ambiente usando `conda activate manim`.
4. Installa manimgl usando `pip install -e .`.


## Utilizzare Manim
Prova ad eseguire il seguente comando:
```sh
manimgl example_scenes.py OpeningManimExample
```
Dovrebbe apparire una finestra che riproduce una semplice scena.

Dai un'occhiata alle [scene di esempio](https://3b1b.github.io/manim/getting_started/example_scenes.html) per vedere esempi della sintassi della libreria, dei tipi di animazione e dei tipi di oggetti. Nel repository [3b1b/videos](https://github.com/3b1b/videos) puoi vedere tutto il codice dei video di 3blue1brown, sebbene il codice dei video più vecchi potrebbe non essere compatibile con la versione più recente di manim. Il readme di quel repository delinea anche alcuni dettagli su come configurare un workflow più interattivo, come mostrato in [questo video demo di manim](https://www.youtube.com/watch?v=rbu7Zu5X1zI), ad esempio.

Quando esegui tramite CLI, alcuni flag utili includono:
* `-w` per scrivere la scena su un file
* `-o` per scrivere la scena su un file e aprire il risultato
* `-s` per saltare alla fine e mostrare solo il frame finale.
    * `-so` salverà il frame finale come immagine e lo mostrerà
* `-n <number>` per saltare all'n-esima animazione di una scena.
* `-f` per rendere la finestra di riproduzione a tutto schermo

Dai un'occhiata a custom_config.yml per un'ulteriore configurazione. Per aggiungere le tue personalizzazioni, puoi modificare questo file, o aggiungere un altro file con lo stesso nome "custom_config.yml" nella directory da cui stai eseguendo manim. Per esempio [questo è quello](https://github.com/3b1b/videos/blob/master/custom_config.yml) per i video di 3blue1brown. Lì puoi specificare dove i video dovrebbero essere esportati, dove manim dovrebbe cercare i file immagine e i suoni che vuoi leggere, e altre impostazioni predefinite riguardanti lo stile e la qualità video.

### Documentazione
La documentazione è in fase di sviluppo su [3b1b.github.io/manim](https://3b1b.github.io/manim/). Esiste anche una versione cinese mantenuta da [**@manim-kindergarten**](https://manim.org.cn): [docs.manim.org.cn](https://docs.manim.org.cn/) (in cinese).

[manim-kindergarten](https://github.com/manim-kindergarten/) ha scritto e raccolto alcune classi extra utili e alcuni codici di video nel [repository manim_sandbox](https://github.com/manim-kindergarten/manim_sandbox).


## Contribuire
È sempre benvenuto. Come menzionato sopra, la [community edition](https://github.com/ManimCommunity/manim) ha l'ecosistema più attivo per i contributi, con testing e integrazione continua, ma le pull request sono benvenute anche qui. Per favore, spiega la motivazione di una determinata modifica e fornisci esempi del suo effetto.


## Licenza
Questo progetto ricade sotto la licenza MIT.
