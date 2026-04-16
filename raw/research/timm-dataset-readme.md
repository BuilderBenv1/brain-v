# Archetype: Voynich Palaeography

A palaeographic database of the Voynich Manuscript (Beinecke MS 408) built with the [Archetype framework](https://github.com/kcl-ddh/digipal) (formerly DigiPal), developed at King's Digital Lab, King's College London.

This database is a supplement to the paper:

> Torsten Timm, "One Hand, Five Labels: A Critical Examination of the Five-Scribe Hypothesis for the Voynich Manuscript" (forthcoming)

## Contents

The database contains structured palaeographic annotations for the Voynich Manuscript:

- **203 manuscript images** covering the major sections of the manuscript
- **1,684 annotated graphs** (images of individual letter forms)
- **8 scribal hands** corresponding to the major sections of the manuscript
- **5 allograph categories** selected as diagnostically significant letter forms

### Hands

| Hand | Scribe |
|------|--------|
| HerbalA | Scribe 1 |
| Pharma | Scribe 1 |
| HerbalB | Scribe 2 |
| Balneology | Scribe 2 |
| Herbal - Scribe 3 | Scribe 3 |
| Stars | Scribe 3 |
| Cosmological | Scribe 4 |
| Scribe 5 | Scribe 5 |

The hand labels follow the section-based classification proposed by Lisa Fagin Davis, where different sections of the manuscript have been attributed to different scribes.

### Allographs

The following allograph categories have been annotated across all hands:

- **iin** — a frequently occurring glyph sequence
- **in** — a common glyph sequence
- **k** — a bench-shaped glyph
- **sh** — a glyph combination
- **weirdos** — unusual or rare glyphs that do not fit standard EVA categories

These allographs were selected because they are diagnostically significant for distinguishing (or, as argued in the accompanying paper, failing to distinguish) scribal hands.

## Manuscript images

The manuscript images are derived from the high-resolution scans provided by the Beinecke Rare Book & Manuscript Library, Yale University. The original digital facsimile is freely available at:

https://collections.library.yale.edu/catalog/2002046

**Please note:** The manuscript images are provided here solely to enable the Archetype database to function. The images remain subject to the terms of use of the Beinecke Rare Book & Manuscript Library, Yale University.

## Installation

This dataset is designed to be imported into an existing Archetype Docker instance. You will need Docker installed on your machine.

### Step 1: Start a fresh Archetype container

```bash
docker pull kingsdigitallab/archetype:latest
docker run -d --name archetype \
  -v ~/archetype/digipal_project:/home/digipal/digipal_project:cached \
  -p 9080:80 \
  kingsdigitallab/archetype:latest
```

Wait until the container has fully started. You can check the logs:

```bash
docker logs -f archetype
```

### Step 2: Extract the data archive

Extract the contents of this dataset into the `digipal_project` directory that is mounted into the container:

```bash
# Extract the database and project files
tar -xzf archetype-voynich-palaeography-project.tar.gz -C ~/archetype/digipal_project/

# Extract the images (separate archive due to size)
tar -xzf archetype-voynich-palaeography-images.tar.gz -C ~/archetype/digipal_project/
```

### Step 3: Import the database

```bash
# Open a shell inside the container
docker exec -it archetype bash

# Import the database dump
psql -U app_digipal -d digipal -f /home/digipal/digipal_project/archetype.sql

# Exit the container shell
exit
```

### Step 4: Restart and browse

```bash
docker restart archetype
```

Open your browser at: http://localhost:9080

You should see the Archetype interface with the Voynich Manuscript data, including the annotated graphs and scribal hand classifications.

The public-facing pages (search, image viewer, graphs overview) do not require a login. To access the admin interface for viewing or editing the underlying data, navigate to http://localhost:9080/admin/ and use the default credentials:

- **Username:** admin
- **Password:** admin

## File structure

```
digipal_project/
├── archetype.sql              # PostgreSQL database dump (annotations, metadata)
├── customisations/            # Project-specific customisations
│   └── static/
│       └── digipal_text/
│           └── viewer/
│               └── tinymce_custom.css
├── images/                    # Manuscript images (TIF format)
│   └── jp2/
│       └── admin-upload/
│           ├── 0/
│           ├── 1/
│           └── ...
├── settings.py                # Project settings
└── media/                     # Generated thumbnails and crops
```

## Technical details

- **Framework:** Archetype 2.7 (Docker image: `kingsdigitallab/archetype:latest`)
- **Database:** PostgreSQL
- **Image server:** IIPImage (integrated in the Docker container)
- **Image format:** TIFF (converted to JPEG2000 internally by Archetype)

## Related publications

- Torsten Timm, "One Hand, Five Labels: A Critical Examination of the Five-Scribe Hypothesis for the Voynich Manuscript" (forthcoming)
- Torsten Timm, "The Challenge of Analyzing a Dynamic Text: Why the Voynich Manuscript Resists Conventional Interpretation" (2025). Available at: https://lingbuzz.net/lingbuzz/009784
- Torsten Timm and Andreas Schinner, "A possible generating algorithm of the Voynich Manuscript" (2020). Cryptologia, 44(3), 231–252.

## Author

Torsten Timm
https://independent.academia.edu/TorstenTimm

## License

The palaeographic annotations and database are licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

The manuscript images are provided by the Beinecke Rare Book & Manuscript Library, Yale University, and are subject to their terms of use.

The Archetype framework is open-source software developed by King's Digital Lab, King's College London.
