import ReactECharts from 'echarts-for-react';

function PieChart({ chart, data = [] }) {
  const pieData = data.map((item) => ({
    name: item[chart.group_by],
    value: item.value,
  }));

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)',
    },

    legend: {
      type: 'scroll',
      orient: 'horizontal',
      bottom: 0,
      textStyle: {
        color: '#64748b',
      },
    },

    series: [
      {
        name: chart.group_by,
        type: 'pie',
        radius: ['45%', '72%'],
        center: ['50%', '45%'],

        avoidLabelOverlap: true,

        itemStyle: {
          borderRadius: 8,
          borderColor: '#ffffff',
          borderWidth: 3,
        },

        label: {
          show: false,
        },

        emphasis: {
          scale: true,
          scaleSize: 8,

          label: {
            show: true,
            fontSize: 14,
            fontWeight: 600,
          },
        },

        labelLine: {
          show: false,
        },

        data: pieData,

        animationType: 'scale',
        animationDuration: 800,
      },
    ],
  };

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
