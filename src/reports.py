import datetime
import os
import time

import jinja2

from src.data_fetcher import DataFetcher
from src.stats import StatsAggregator

class BaseReportGenerator(object):

    def __init__(self, template_file, output_filename):
        self.jinja_template = self._prepare_jinja_template(template_file)
        self.output_filename = output_filename

    @staticmethod
    def _prepare_jinja_template(template_file):
        this_dir = os.path.dirname(os.path.abspath(__file__))
        template_dir = os.path.join(this_dir, 'templates')
        loader = jinja2.FileSystemLoader(template_dir)
        jinja_env = jinja2.Environment(loader=loader)
        return jinja_env.get_template(template_file)

    @staticmethod
    def _write_file(filename, content):
        # TODO: wrap with try/catch
        f = open(filename, 'w')
        f.write(content)
        f.close()

    @staticmethod
    def _get_context():
        raise NotImplementedError

    def generate_report(self):
        rendered_report = self.jinja_template.render(**self._get_context())
        output_file = 'output/{}'.format(self.output_filename)
        self._write_file(output_file, rendered_report)


class PullRequestsListReport(BaseReportGenerator):

    def __init__(self):
        super(PullRequestsListReport, self).__init__(
            template_file='pull_requests_list.html',
            output_filename='pull_requests_list_report.html',
        )

    @staticmethod
    def _get_context():
        return {
            'pull_requests': DataFetcher().get_pull_requests(),
        }


class CreatedMergedPRsReport(BaseReportGenerator):

    def __init__(self):
        super(CreatedMergedPRsReport, self).__init__(
            template_file='created_merged_prs.html',
            output_filename='created_merged_prs_report.html',
        )

    @staticmethod
    def _format_data(count_dict):
        data = []
        for date in count_dict:
            timestamp = time.mktime(date.timetuple())*1000
            count = count_dict[date]
            data.append([timestamp, count])
        return data

    @classmethod
    def _get_context(cls):
        aggregator = StatsAggregator()
        created_prs = cls._format_data(aggregator.prs_opened_by_day())
        merged_prs = cls._format_data(aggregator.prs_merged_by_day())

        return {
            'created_prs': created_prs,
            'merged_prs': merged_prs,
        }

if __name__ == '__main__':

    # pull requests list report
    report_generator = PullRequestsListReport()
    report_generator.generate_report()

    # opened/closed PRs report
    report_generator = CreatedMergedPRsReport()
    report_generator.generate_report()

