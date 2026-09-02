# OEM Intelligence Dashboard POC

Live URL after GitHub Pages is enabled:

https://chasenickleson.github.io/oem-intelligence-dashboard/

## Initial setup

1. Upload all files and folders in this package to the repository root.
2. In Settings > Pages, select **Deploy from a branch**, branch **main**, folder **/(root)**, then Save.
3. In Settings > Actions > General, under Workflow permissions select **Read and write permissions**, then Save.
4. Open Actions > Refresh dashboard data > Run workflow.
5. Wait for the workflow and Pages deployment to complete.

## Automation

- Weekly refresh: Mondays at 11:15 UTC.
- Monthly fallback refresh: first day of each month at 11:30 UTC.
- Manual refresh: Actions > Refresh dashboard data > Run workflow.
- The browser loads dashboard-data.json with cache bypass whenever the dashboard opens.

## POC limitations

Google News RSS is used as the no-key public news aggregator. Publisher availability and titles may change. The workflow validates output and retains prior segment data when a feed fails. Scores are intentionally stable in this POC; newsroom and leadership topics update automatically.
