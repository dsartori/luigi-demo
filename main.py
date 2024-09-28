import luigi
import luigi.db_task_history
from tasks import GenerateReport

if __name__ == "__main__":
    luigi.build([GenerateReport()], local_scheduler=False)
