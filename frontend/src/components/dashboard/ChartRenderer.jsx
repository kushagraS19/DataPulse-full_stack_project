import BarChart from './BarChart';
import LineChart from './LineChart';
import PieChart from './PieChart';
import ScatterChart from './ScatterChart';

function ChartRenderer({ chart, data }) {
  if (!chart) {
    return (
      <div className='flex min-h-[280px] items-center justify-center text-sm text-slate-500'>
        No chart configuration available.
      </div>
    );
  }

  switch (chart.chart_type) {
    case 'bar':
      return <BarChart chart={chart} data={data} />;

    case 'line':
      return <LineChart chart={chart} data={data} />;

    case 'pie':
      return <PieChart chart={chart} data={data} />;

    case 'scatter':
      return <ScatterChart chart={chart} data={data} />;

    default:
      return (
        <div className='flex min-h-[280px] items-center justify-center rounded-xl border border-dashed border-slate-300 text-sm text-slate-500 dark:border-slate-700'>
          Unsupported chart type:{' '}
          <span className='ml-1 font-medium'>{chart.chart_type}</span>
        </div>
      );
  }
}

export default ChartRenderer;
