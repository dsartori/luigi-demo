# Luigi Demo
This repository contains a simple demo of [Luigi](https://github.com/spotify/luigi), a Python module for running complex pipelines of batch jobs.

## Installation

To get started with this project, clone the repository and build the Docker container:

```bash
git clone https://github.com/dsartori/luigi-demo.git
cd luigi-demo
docker build -t luigi-demo .
```

## Usage

To run the Luigi pipeline, first start the Docker container:

```bash
docker run -d --name luigi-demo-container -p 8082:8082 luigi-demo
```

The container runs the Luigi central scheduler. You can visualize the pipeline by navigating to `http://localhost:8082` in your browser.

Open a terminal session in the container:

```bash
docker exec -it luigi-demo-container /bin/bash
```

Execute the **GenerateReport** task and all its dependencies:
```bash
python /app/main.py
```

View the report output:
```bash
cat /app/output/expense_report.csv
```


# Demo Details

This demo uses Luigi to run a short workflow of dependent tasks and populate a local SQLite database from multiple sources.

The resulting data tables are queried to generate a CSV report saved in  `/app/output`.

### Tasks

Three [Tasks](https://luigi.readthedocs.io/en/stable/tasks.html) are defined in `/app/tasks.py`:

- **FetchRates** loads Exchange rate data from the [Bank of Canada Valet API](https://www.bankofcanada.ca/valet/)
- **ImportExpenses** loads expense data from a CSV of dummy expenses
- **GenerateReport** generates a CSV report joining the loaded data

Each task must provide an output [Target](https://luigi.readthedocs.io/en/stable/targets.html) for the Luigi task [Scheduler](https://luigi.readthedocs.io/en/stable/central_scheduler.html) to determine the task's outcome. The database tasks in this demo register their Luigi Task ID in `/tmp` on completion. The reporting task's target is the output CSV.

### Database

The database tables are defined in `expenses.sql`. The database file `/app/expenses.db` is generated with SQLite when the container is built.

### Luigi Server

Running the container starts the `luigid` service. `/app/luigi.cfg` is its configuration file.




