import ReactECharts from 'echarts-for-react';

function PieChart({ chart, data = [] }) {
  const pieData = data
    .map((item) => ({
      name: item[chart.group_by],
      value: Number(item.value),
    }))
    .filter((item) => item.name !== undefined && Number.isFinite(item.value));

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
      formatter: (params) =>
        `<strong>${params.name}</strong><br/>Value: ${params.value}<br/>Share: ${params.percent}%`,
    },

    legend: {
      type: 'scroll',
      orient: 'horizontal',
      bottom: 0,
      left: 'center',
      itemGap: 14,
      textStyle: {
        color: '#64748b',
        fontSize: 11,
      },
    },

    series: [
      {
        name: chart.group_by || chart.operation || 'Value',
        type: 'pie',
        radius: ['45%', '72%'],
        center: ['50%', '44%'],
        avoidLabelOverlap: true,

        itemStyle: {
          borderRadius: 8,
          borderColor: '#ffffff',
          borderWidth: 3,
          shadowBlur: 10,
          shadowColor: 'rgba(15, 23, 42, 0.08)',
        },

        label: {
          show: false,
        },

        emphasis: {
          scale: true,
          scaleSize: 8,
          itemStyle: {
            shadowBlur: 18,
            shadowColor: 'rgba(15, 23, 42, 0.16)',
          },
          label: {
            show: true,
            color: '#0f172a',
            fontSize: 14,
            fontWeight: 600,
            formatter: '{b}\n{d}%',
          },
        },

        labelLine: {
          show: false,
        },

        data: pieData,

        animationType: 'expansion',
        animationDuration: 900,
        animationEasing: 'cubicOut',
        animationDelay: (idx) => idx * 45,
      },
    ],
  };

  if (!pieData.length) {
    return (
      <div className='flex h-[300px] items-center justify-center rounded-xl border border-dashed border-stone-200 bg-stone-50/60 text-sm text-slate-500'>
        No data available for this chart.
      </div>
    );
  }

  return (
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
  );
}

export default PieChart;
