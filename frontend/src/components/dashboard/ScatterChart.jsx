import ReactECharts from 'echarts-for-react';

function ScatterChart({ chart, data = [] }) {
  const scatterData = data
    .map((item) => [Number(item[chart.x_column]), Number(item[chart.y_column])])
    .filter(([x, y]) => Number.isFinite(x) && Number.isFinite(y));

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        const [x, y] = params.value;

        return `
                    <strong>${chart.x_column}</strong>: ${x}<br/>
                    <strong>${chart.y_column}</strong>: ${y}
                `;
      },
    },

    grid: {
      top: 30,
      right: 25,
      bottom: 55,
      left: 65,
      containLabel: true,
    },

    xAxis: {
      type: 'value',
      name: chart.x_column,
      nameLocation: 'middle',
      nameGap: 35,

      axisLabel: {
        color: '#64748b',
      },

      nameTextStyle: {
        color: '#64748b',
      },

      splitLine: {
        lineStyle: {
          color: '#e2e8f0',
          type: 'dashed',
        },
      },
    },

    yAxis: {
      type: 'value',
      name: chart.y_column,
      nameLocation: 'middle',
      nameGap: 50,

      axisLabel: {
        color: '#64748b',
      },

      nameTextStyle: {
        color: '#64748b',
      },

      splitLine: {
        lineStyle: {
          color: '#e2e8f0',
          type: 'dashed',
        },
      },
    },

    series: [
      {
        name: `${chart.x_column} vs ${chart.y_column}`,
        type: 'scatter',
        data: scatterData,

        symbolSize: 10,

        emphasis: {
          focus: 'series',
          scale: true,
        },

        animationDuration: 800,
        animationEasing: 'cubicOut',
      },
    ],
  };

  return (
    <div className='relative'>
      <ReactECharts
        option={option}
        style={{
          width: '100%',
          height: '300px',
        }}
        opts={{
          renderer: 'canvas',
        }}
        notMerge={true}
        lazyUpdate={true}
      />

      {chart.correlation !== undefined && (
        <div className='absolute right-2 top-2 rounded-lg bg-slate-100 px-3 py-1.5 text-xs font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-300'>
          Correlation: {Number(chart.correlation).toFixed(2)}
        </div>
      )}
    </div>
  );
}

export default ScatterChart;
