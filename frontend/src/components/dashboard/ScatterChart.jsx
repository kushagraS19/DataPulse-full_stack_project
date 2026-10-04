import ReactECharts from 'echarts-for-react';

function ScatterChart({ chart, data = [] }) {
  const scatterData = data
    .map((item) => [Number(item[chart.x_column]), Number(item[chart.y_column])])
    .filter(([x, y]) => Number.isFinite(x) && Number.isFinite(y));

  const option = {
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(255, 255, 255, 0.96)',
      borderColor: '#e7e5e4',
      borderWidth: 1,
      padding: [10, 12],
      textStyle: {
        color: '#334155',
        fontSize: 12,
      },
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
        fontSize: 11,
      },

      nameTextStyle: {
        color: '#64748b',
        fontSize: 11,
        fontWeight: 500,
      },

      axisLine: {
        lineStyle: {
          color: '#e7e5e4',
        },
      },

      axisTick: {
        show: false,
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
        fontSize: 11,
      },

      nameTextStyle: {
        color: '#64748b',
        fontSize: 11,
        fontWeight: 500,
      },

      axisLine: {
        show: false,
      },

      axisTick: {
        show: false,
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

        symbol: 'circle',
        symbolSize: 10,

        itemStyle: {
          borderColor: '#ffffff',
          borderWidth: 1.5,
          shadowBlur: 8,
          shadowColor: 'rgba(15, 23, 42, 0.12)',
        },

        emphasis: {
          focus: 'series',
          scale: 1.35,
          itemStyle: {
            shadowBlur: 16,
            shadowColor: 'rgba(15, 23, 42, 0.18)',
          },
        },

        animationDuration: 900,
        animationEasing: 'cubicOut',
        animationDelay: (idx) => Math.min(idx * 12, 500),
      },
    ],
  };

  if (!scatterData.length) {
    return (
      <div className='flex h-[300px] items-center justify-center rounded-xl border border-dashed border-stone-200 bg-stone-50/60 text-sm text-slate-500'>
        No valid numeric data available for this chart.
      </div>
    );
  }

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
        <div className='pointer-events-none absolute right-2 top-2 rounded-lg border border-stone-200/80 bg-white/90 px-3 py-1.5 text-xs font-medium text-slate-600 shadow-sm backdrop-blur-sm'>
          Correlation: {Number(chart.correlation).toFixed(2)}
        </div>
      )}
    </div>
  );
}

export default ScatterChart;
