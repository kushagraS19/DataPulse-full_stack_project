import ReactECharts from 'echarts-for-react';

function BarChart({ chart, data = [] }) {
  const categories = data.map((item) => item[chart.group_by]);
  const values = data.map((item) => item.value);
  const hasData = data.length > 0;

  const option = {
    animation: true,
    animationDuration: 850,
    animationEasing: 'cubicOut',

    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.96)',
      borderColor: '#e7e5e4',
      borderWidth: 1,
      padding: [10, 12],
      extraCssText:
        'box-shadow: 0 12px 30px rgba(15, 23, 42, 0.10); border-radius: 10px;',
      textStyle: {
        color: '#334155',
        fontSize: 12,
      },
      axisPointer: {
        type: 'shadow',
        shadowStyle: {
          color: 'rgba(100, 116, 139, 0.08)',
        },
      },
    },

    grid: {
      top: 24,
      right: 20,
      bottom: categories.length > 8 ? 64 : 42,
      left: 56,
      containLabel: true,
    },

    xAxis: {
      type: 'category',
      data: categories,
      boundaryGap: true,

      axisLabel: {
        color: '#64748b',
        fontSize: 11,
        margin: 12,
        rotate: categories.length > 6 ? 35 : 0,
        hideOverlap: true,
      },

      axisLine: {
        lineStyle: {
          color: '#e7e5e4',
        },
      },

      axisTick: {
        show: false,
      },
    },

    yAxis: {
      type: 'value',

      axisLabel: {
        color: '#64748b',
        fontSize: 11,
        margin: 10,
      },

      axisLine: {
        show: false,
      },

      axisTick: {
        show: false,
      },

      splitLine: {
        lineStyle: {
          color: '#f1f0ef',
          type: 'dashed',
        },
      },
    },

    series: [
      {
        name: chart.column || chart.operation || 'Value',
        type: 'bar',
        data: values,

        barMaxWidth: 42,
        barMinHeight: 3,
        showBackground: true,
        backgroundStyle: {
          color: 'rgba(241, 245, 249, 0.55)',
          borderRadius: [6, 6, 0, 0],
        },

        itemStyle: {
          color: '#64748b',
          borderRadius: [7, 7, 2, 2],
          shadowBlur: 8,
          shadowColor: 'rgba(15, 23, 42, 0.10)',
          shadowOffsetY: 3,
        },

        emphasis: {
          focus: 'series',
          scale: true,

          itemStyle: {
            color: '#475569',
            shadowBlur: 16,
            shadowColor: 'rgba(15, 23, 42, 0.18)',
            shadowOffsetY: 4,
          },
        },

        animationDelay: (index) => index * 45,
        animationDuration: 650,
        animationEasing: 'cubicOut',
      },
    ],
  };

  if (!hasData) {
    return (
      <div className='flex h-[300px] items-center justify-center rounded-xl border border-dashed border-stone-200 bg-stone-50/50 text-sm text-slate-500'>
        No chart data available.
      </div>
    );
  }

  return (
    <div className='w-full overflow-hidden rounded-xl transition-transform duration-300'>
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
    </div>
  );
}

export default BarChart;
