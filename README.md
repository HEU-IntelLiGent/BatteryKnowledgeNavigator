# IntelLiGent Battery Knowledge Navigator

> [!NOTE]
> This repository is no longer under active development. The Battery Knowledge Navigator has been integrated into the [Battery Genome](https://www.battery-genome.org), which now provides its long-term support and hosting. The IntelLiGent project has its own page there at [battery-genome.org/projects/g-101069765](https://www.battery-genome.org/projects/g-101069765). If you want IntelLiGent data or plan to build on this work, start there. The code below stays online as a record of the prototype built during the project.

The Battery Knowledge Navigator is a Streamlit app for managing battery research data, written in the Horizon Europe project IntelLiGent (2022 to 2026). Descriptive metadata about materials, components and cells is stored as RDF in a Blazegraph triple store and annotated with terms from the [BattINFO](https://github.com/BIG-MAP/BattINFO) ontology. Cycling data from Maccor test files goes into PostgreSQL. The app lets you browse and edit the knowledge graph, add entries through forms generated from JSON schemas, and plot cycling results.

## What's in the app

- `explore.py` is the entry point. Pick one or more terms by label and each opens in a tab with its IRI, elucidation, annotation properties and named individuals; an edit toggle writes changes back to Blazegraph.
- The New Entry page renders a form from each JSON schema in `data/schema/` (active material, binder, conductive additive, current collector, electrode, electrolyte, separator, pouch cell) and stores the submission as triples. Its Dataset option uploads Maccor CSV exports to PostgreSQL.
- Cycling data is plotted per cell on the Data Dashboard, with optional end-of-life lines at 80% of initial capacity and z-score outlier filtering.
- Two pages were never finished. Query Builder is a prototype that assembles SPARQL queries against Wikidata, and SPARQL Endpoint is an empty placeholder.

Shared helpers for SPARQL, form generation and database access live in `tools/`.

## Running it locally

You need Python 3.10 or 3.11, a [Blazegraph](https://github.com/blazegraph/database) server loaded with BattINFO and the project data, and a PostgreSQL database with `cycle`, `form` and `stats` tables. Neither the triple store contents nor the database schema are included in this repository.

```bash
git clone https://github.com/HEU-IntelLiGent/BatteryKnowledgeNavigator.git
cd BatteryKnowledgeNavigator
python -m venv .venv
source .venv/bin/activate        # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run explore.py
```

Dependencies are pinned to 2023 releases, from the period the app was developed in. Newer Streamlit versions have removed some of the APIs it calls.

Connection settings are read from environment variables. The PostgreSQL ones are the standard libpq variables, so a `~/.pgpass` file works for the password as well.

| Variable | Default |
| --- | --- |
| `BLAZEGRAPH_URL` | `http://localhost:9999/blazegraph/sparql` |
| `PGHOST` | `localhost` |
| `PGPORT` | `5432` |
| `PGDATABASE` | `heu-intelligent` |
| `PGUSER` | `postgres` |
| `PGPASSWORD` | none |

## License

Released under the MIT License, see [LICENSE](LICENSE). Versions of this repository before October 2026 were published under GPL-3.0.

## Acknowledgements

IntelLiGent received funding from the European Union's Horizon Europe research and innovation programme under grant agreement No 101069765. Thanks to the H2020 project BIG-MAP for the BattINFO ontology.
